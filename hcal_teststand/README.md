# Description of test stand modules 

## μHTR

#### Classes

**link** -- *An object that represents a uHTR link. It contains information about what it's connected to.*

constructors:

<pre>
def __init__(self, ts="uknown", uhtr_slot=-1, link_number=-1, qie_unique_id="unknown", qie_half=-1, qie_fiber=-1, on=False)
</pre>
data members:  

 - get_data -- *??*
<pre>
def get_data(self)
</pre>
 - Print -- *prints out information about the link, ip address of μHTR, μTCA slot, QIE card ID, IGLOO2, frontend fiber number, active or not.*
<pre>
def Print(self)
</pre>
methods: 

#### Functions

 - **send_commands** -- *Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.*
<pre>
def send_commands(ts, uhtr_slot, cmds)
</pre>
 - **send_commands_script** -- *Sends commands to "uHTRtool.exe" and returns the raw output and a log. The input is a teststand object and a list of commands.*
<pre>
def send_commands_script(ts, uhtr_slot, cmds)
</pre>
 - **get_info_ip** -- *Returns a dictionary of information about the uHTR, such as the FW versions.*
<pre>
def get_info_ip(ts, uhtr_slot)	
</pre>
 - **get_info** -- *A get_info function that accepts either an IP address or a teststand object.*
<pre>
def get_info(ip_or_ts)
</pre>
 - **get_status** -- *Perform basic checks with the uHTRTool.exe* 
<pre>
def get_status(ts)
</pre>
 - **parse_links** --  *Parses the raw ouput of the uHTRTool.exe. Commonly, you use the "find_links" function below, which uses this function.*
<pre>
def parse_links(raw)
</pre>
 - **parse_links_full** -- *Parses the raw ouput of the uHTRTool.exe. Commonly, you use the "find_links" function below, which uses this function.*
<pre>
def parse_links_full(raw)
</pre>
 - **find_links** -- *Initializes links and then returns a list of link indicies, for a certain uHTR.*
<pre>
def find_links(ts, uhtr_slot)
</pre>
 - **find_links_full** -- *Initializes links and then returns a list of link indicies, for a certain uHTR.*
<pre>
def find_links_full(ts, uhtr_slot)
</pre>
 - **get_links** -- *Initializes and sets up links of a uHTR and then returns a list of links.*
<pre>
def get_links(ts, uhtr_slot)
</pre>
 - **get_links_all** -- *Calls "get_links" for all uHTRs in the system.* 
<pre>
def get_links_all(ts)
</pre>
 - **get_histo** -- **
<pre>
def get_histo(ts, uhtr_slot, n , sepCapID , fileName )
</pre>
 - **get_data** -- **
<pre>
def get_data(ts, uhtr_slot, n, ch)
</pre>
 - **get_triggered_data** -- **
<pre>
def get_triggered_data(ts, uhtr_slot , n , outputFile="testTriggeredData")
</pre>
 - **parse_data** -- *From raw uHTR SPY data, return a list of adcs, cids, etc. organized into sublists per fiber.*
<pre>
def parse_data(raw)
</pre>
 - **get_data_parsed** -- **
<pre>
def get_data_parsed(ts, uhtr_slot, n, ch)
</pre>
> Written with [StackEdit](https://stackedit.io/).