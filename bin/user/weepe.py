#
# AGWPE weewx extension for sending APRS packets to a AGWPE host.
# The host is usually something like Direwolf which will forward
# the packet to APRSIS and/or RF. This extension simply binds 
# weewx to the host for weather station reporting.
#
# Requires:
# 'aprs' weewx extension        -- build APRS packets from weewx generated weather reports.
# 'pyham_pe' package            -- Python AGWPE module
#
#  More information about AGWPE can be found at https://www.on7lds.net/42/sites/default/files/AGWPEAPI.HTM
#
# NOTE - this module is a subclass of aprs. If the aprs extension is not installed, then weepe will
# trace / log an error but weewx will continue normally.

import logging
import os
import importlib.util
import pe.app
import weewx.engine
import threading
import queue
import pe
import socket

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# log_stream_debug = logging.StreamHandler()
# log_stream_debug.setLevel(logging.DEBUG)
# log_stream_debug.setFormatter(logging.Formatter("%(message)s"))
# log.addHandler(log_stream_debug)

try:
    # import aprs module - it's expected that all extensions reside in the
    # same directory.
    aprs_path = os.path.abspath(os.path.dirname(__file__)) + '/aprs.py'
    spec = importlib.util.spec_from_file_location('APRS', aprs_path)
    aprs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aprs)

    class AGWPEWx(aprs.APRS, weewx.engine.StdService):

        def __init__(self, engine, config_dict):
            super().__init__(engine, config_dict)

            try:
                conf = config_dict['AGWPEWX']
            except KeyError:
                log.error("Configuration not found..aborting")
            else:
                self._callsign = str.upper(conf.get("callsign", "NOCALL"))
                self._via = conf.get("via", "WIDE2-1").split(',')
                self._dest = str.upper(conf.get("dest", "APRS"))
                self._host = conf.get("host", "localhost")
                self._port = int(conf.get("port", 8000))
                self._interval = int(conf.get("interval", 0))

                for s in self._via:
                    s = str.upper(s)

                if self._callsign == "NOCALL":
                    log.info("Test mode")
                    return

                log.info("Starting")

                # Set to the interval value to emit a packet on the first
                # archive packet after start up.
                self._interval_count = self._interval

                self._pktEngine = pe.app.Application()

                self._check_pe_engine()

                self._pkt_queue = queue.Queue()

                # This should be last
                self._agwpe = threading.Thread(target=self._agwpe_handler, daemon=True)
                self._agwpe.start()

        # Protected methods
        # override aprs._handle_new_archive_record
        def _handle_new_archive_record(self, event):
            super()._handle_new_archive_record(event)

            if self._callsign != "NOCALL":
                # Read the packet in and queue it up
                # The super doesn't handle file execptions so if saving it didn't work
                # we'll probably crash, but handle exceptions here anyway.
                try:
                    f = open(self._output_filename)
                except IOError:
                    log.error("File error")
                else:
                    pkt = f.read()
                    self._pkt_queue.put(pkt)
                    f.close()
        
        # AGWPE thread context (also called once from the constructor before the thread is instantiated)
        def _check_pe_engine(self):
            ret = True

            if self._pktEngine.engine is None:
                log.debug("Using host %s:%d", self._host, self._port)

                try:
                    # Doing this because pe doesn't set a timeout on its socket and
                    # it expects it to block indefinitely waiting on a response.
                    # The default timeout is set in the weewx engine and possibly in
                    # drivers as well. Setting this here ensures that pe will have what
                    # it expects when it creates the AGWPE socket.
                    # The real fix is to either handle the TimeoutError exception or to set
                    # the timeout on the socket itself; simple changes but in the pe package.
                    socket.setdefaulttimeout(None)

                    self._pktEngine.start(self._host, self._port)
                    self._pktEngine.register_callsigns(self._callsign)
                except socket.gaierror:
                    log.error("Host name not found")
                    ret = False
                except ConnectionRefusedError:
                    log.error("Connection refused")
                    ret = False

            return ret
            
        # AGWPE thread context
        def _agwpe_handler(self):
            log.info("Starting AGPWPE thread..")

            while True:
                pkt = self._pkt_queue.get()
                log.debug("packet: '" + pkt + "'")

                self._interval_count += 1
                if self._interval_count > self._interval:
                
                    try:
                        if self._check_pe_engine() is True:
                            self._pktEngine.send_unproto(port=0,
                                                        call_from=self._callsign,
                                                        call_to=self._dest,
                                                        data=pkt,
                                                        via=self._via)
                        else:
                            log.warning("Not connected to server")
                    except pe.app.NotConnectedError:
                        log.error("Connection to server lost")
                    except ValueError:
                        log.error("Bad packet")

                    self._pkt_queue.task_done()
                    self._interval_count = 0
                    
except FileNotFoundError:
    class AgwpeWx():

        def __init__(self, engine, config_dict):
            log.error("APRS Extension not found..disabling")

