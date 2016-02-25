#
# (c) 2015 dray <dresen@itsecteam.ms>
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License or any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License
# see <http://www.gnu.org/licenses/>.
#

from subprocess import check_output
import json
import sys

class JsonManager:
    def __init__(self):
        self.json158 = []
        self.json159 = []
        self.result = {}
        pass

    def loadJson(self):
        data=""
        for l in open("alfred_158.json"):
            data += l
        self.json158 = json.loads(data)
        data=""
        for l in open("alfred_159.json"):
            data += l
        self.json159 =json.loads(data)

    def loadJsonFromAlfred(self, socket):
        self.json158 = json.loads(check_output(["alfred-json", "-z","-r","158","-s",socket]).decode("utf-8"))
        self.json159 = json.loads(check_output(["alfred-json", "-z","-r","159","-s",socket]).decode("utf-8"))

    def processJson159(self):
        self.result['nodes'] = {}
        self.result['totalclients']=0
        for id in self.json159:
            mac = id
            node = self.json159[id]

    # Nodes/Gateway
            try:
                if 'mesh_vpn' in node and 'backbone' in node['mesh_vpn']['groups']:
                    peers = node['mesh_vpn']['groups']['backbone']['peers']
                    for x in peers:
                        if peers[x]:
                            self.__incCounter__('gateway',x)
            except:
                pass
                sys.stderr.write("Error %s" % sys.exc_info()[0])

    # Client/Node
            try:
                id = node['node_id']
                self.result['nodes'][id] = {}
                if 'clients' in node:
                    self.result['nodes'][id]["count"] = node['clients']['total']
                if 'advanced-stats' in self.json158[mac]:
                    if 'store-stats' in self.json158[mac]['advanced-stats'] and self.json158[mac]['advanced-stats']['store-stats'] == True:
                        self.result['nodes'][id]['advanced'] = self.processAdvancedStats(node)
                    self.result['totalclients'] += node['clients']['total']
            except:
                sys.stderr.write("Error %s" % sys.exc_info()[0])

    def processAdvancedStats(self, node):
        advancedStats = {}

        # add traffic stats
        if 'traffic' in node:
            advancedStats['traffic'] = {}
            if 'rx' in node['traffic'] and 'tx' in node['traffic']:
                advancedStats['traffic']['all'] = self.ifStats(node['traffic']['rx'], node['traffic']['tx'])
            if 'mgmt_rx' in node['traffic'] and 'mgmt_tx' in node['traffic']:
                advancedStats['traffic']['managed'] = self.ifStats(node['traffic']['mgmt_rx'], node['traffic']['mgmt_tx'])
            if 'forward' in node['traffic']:
                advancedStats['traffic']['forward'] = self.ifStats(node['traffic']['forward'])
        return advancedStats


    def ifStats(self,rx,tx = None):
        mapping = {
            'bytes' : 'if_octets',
            'dropped' : 'if_dropped',
            'packets' : 'if_packets'
        }
        ifaceStats = {}
        for k, v in mapping.iteritems():
            if rx and k in rx or tx and k in tx:
                ifaceStats[v] = {}
            if tx:
                try:
                    ifaceStats[v]['rx'] = rx[k]
                except:
                    pass
                try:
                    ifaceStats[v]['tx'] = tx[k]
                except:
                    pass
            else:
                try:
                    ifaceStats[v] = rx[k]
                except:
                    pass
        return ifaceStats


    def processJson158(self):
        self.result["autoupdate"] = 0
        for id in self.json158:
            node = self.json158[id]

    # Nodes/Firmware
            if 'software' in node:
                firmware = node['software']['firmware']['release']
                self.__incCounter__('firmwarecount',firmware)
                if 'autoupdater' in node['software']:
		    branch = node['software']['autoupdater']['branch']
		    self.__incCounter__('branchcount',branch)

		    if node['software']['autoupdater']['enabled']:
			self.__incCounter__('autoupdate')

            if 'hardware' in node:
                hardware = node['hardware']['model']
                self.__incCounter__('hardwarecount',hardware)

            if 'location' in node:
                self.__incCounter__('locationcount')

        self.result['nodecount'] = len(self.json158)

    def __incCounter__ (self, key, value=None):
        if value is None:
            if key not in self.result:
                self.result[key] = 0
            self.result[key]+=1
        else:
            value = self.___cleanstr___(value)
            if key not in self.result:
                self.result[key] = {}
            if value in self.result[key]:
                self.result[key][value]+=1
            else:
                self.result[key][value]=1

    def ___cleanstr___(self, cleanstr):
        specialChars = [" ","+",".","\\","/","-"]
        for char in specialChars:
            cleanstr = cleanstr.replace(char,"_")
        cleanstr = cleanstr.replace(":","")
        return cleanstr

