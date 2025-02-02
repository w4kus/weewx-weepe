## WEEWX AGWPE Packet Engine - *weepe*

This is a [weewx](https://weewx.com/) extension allows you to forward your weather data to an [AGWPE](https://www.on7lds.net/42/sites/default/files/AGWPEAPI.HTM) server for transmission over [APRS](http://www.aprs.org/).  For more information, see the [Wikipedia](https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System) article.

### Requirements
- **aprs** - **weewx** extension which generates the data field of an APRS packet from archive reports.  This can be downloaded [here](https://github.com/cavedon/weewx-aprs) and installed using the **weectl extension** subcommand.
- **pyham_pe** - AGWPE packet engine client Python package. This can be installed using **pip**.

### Configuration
The following configuration items are located in the section in *weewx.conf* labeled **[AGWPEWX]**.
- **host** - the AGWPE host to use. *Default: "localhost"*
- **port** - the IP port to use. *Default: 8000*
- **callsign** - the callsign to use. This will be both the source address of the generated packet and the AGWPE login. *Default: "NOCALL"*
- **via** - the path to insert into the packet. *Default: "WIDE2-1"*
- **dest** - the destination of the packet. *Default: "APRS"* (see below for more information)
- **interval** - the number of archive reports to skip before generating a packet. *Default: 0*

See also the configuration for the **aprs** extension which will allow you to set your station's symbol and comment fields as well as whether or not to generate position or positionless weather packets.

### Packet Generation
**weepe** uses the **weewx**'s archive generation rate as the "clock" to drive the generation of packets. By default, **weewx** uses a 5 minute interval for generating archive records. Therefore, the *interval* configuration item controls how often **weepe** will generate packets. If you are sending your packets to a AGWPE server which transmits the packets over the air, take care in choosing the value of *interval* so as not to generate too much traffic, especially if a wide area digipeater is in range.

For example, generating a packet every 30 minutes is nice rate. Assuming **weewx** is set to generate archive records every 5 minutes, then to generate your weather packets every 30 minutes, set *inteval* to 6. Note that **weepe** will always send a packet when the first archive record is received after startup.

### Configuration Notes
The **dest** item is typically set to one of the character sequence codes as defined [here](http://aprs.org/aprs11/tocalls.txt). These usually describe the hardware and / or software you are using. For example, I currently use [Direwolf](https://github.com/wb2osz/direwolf) version 1.7 for my IGATE software, so my **dest** is set to "APDW17". It is highly recommended to change the **dest** field from the default.

**callsign** MUST be set to a valid amateur radio callsign. Do not use the default.

**via** cannot be empty. If you're unsure about what to set this to, stick with the default. There are many references on APRS paths online.


