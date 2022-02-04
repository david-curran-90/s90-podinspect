#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from colorama import Fore, Style 
from kubernetes import client, config
from prettytable import PrettyTable

__version__ = "0.2.0"
info = Fore.CYAN
err = Fore.RED
rst = Style.RESET_ALL
class outputHandler:
    def __init__(self, verbose, data, output):
        self.outputTable = PrettyTable()
        self.verbose = verbose
        self.data = data
        self.output = output

        # set up the table for PrettyTable()
        self.configureOutputTable()

    def addOutputRow(self, data):
        """
        Adds a row to the table
        """
        try:
            output = [
                data["app"],
                data["pods"],
                data["services"],
                data["ingress"], 
                data["storage"], 
                data["secrets"], 
                data["configs"], 
                data["nodes"]
            ]
            if self.verbose:
                output.append(data["namespace"])
                output.append(data["containers"])
                output.append(data["labels"])
                output.append(data["annotations"])
        
            self.outputTable.add_row(output)
        except Exception as e:
            print(f"{err}Failed to add table row:\n\t{e}{rst}")


    def configureOutputTable(self):
        """
        Configures the field names for PrettyTable()
        """
        defaultFields = ["App", "Pods", "Service", "Ingress", "Storage", "Secrets", "ConfigMaps", "Nodes"]

        if self.verbose:
            defaultFields.extend(["Containers", "Namespace", "Labels", "Annotations"])
        self.outputTable.field_names = defaultFields


    def outputAsTable(self):
        """
        Handles printing the output in table format
        """
        self.addOutputRow(self.data)
        print(self.outputTable)

    
    def outputAsJson(self):
        """
        Handles printing the output in JSON format
        """
        print(f"{err}JSON not yet supported, printing raw{rst}")
        print(f"{self.data}")


    def outputAsPretty(self):
        """
        Handling printinf the output in a pretty, easy to read format
        """
        print(f"{info}App:{rst} {data['app']}")
        if self.verbose:
            print(f"{info}Namespace:{rst} {data['namespace']}")
        print(f"{info}Pods:{rst}")
        for p in data["pods"]:
            print(f"\t{p}")
        print(f"{info}Linked Services:{rst}")
        for s in data["services"]:
            print(f"\t{s}")
        print(f"{info}Linked Ingress resources:{rst}")
        for i in data["ingress"]:
            print(f"\t{i}")
        print(f"{info}Mounted Storage:{rst}")
        for s in data["storage"]:
            if data["storage"][s]:
                print(f"\t{s}s:")
            for p in data["storage"][s]:
                print(f"\t\t{p}")
        print(f"{info}Linked Secrets:{rst}")
        for s in data["secrets"]:
            print(f"\t{s}")
        print(f"{info}Linked ConfigMaps:{rst}")
        for c in data["configs"]:
            print(f"\t{c}")
        print(f"{info}Running on Nodes:{rst}")
        for n in data["nodes"]:
            print(f"\t{n}")
        if self.verbose:
            print(f"{info}Pod Containers:{rst}")
            for c in data["containers"]:
                print(f"\t{c}")
            print(f"{info}Labels:{rst}")
            for l in data["labels"]:
                print(f"\t{l} = {data['labels'][l]}")
            print(f"{info}Annotations:{rst}")
            for a in data["annotations"]:
                print(f"\t{a} = {data['annotations'][a]}")

    def main(self):
        """
        Entrypoint for printing output

        calls different handlers depnding 
        on what output type is speicfied
        """
        if self.output.lower() == "table":
            self.outputAsTable()
        elif self.output.lower() == "raw":
            print(self.data)
        elif self.output.lower() == "json":
            self.outputAsJson()
        elif self.output.lower() == "pretty":
            self.outputAsPretty()
        else:
            print(f"{err}Output type not recognised{rst}")


class appInfo:

    def __init__(self, namespace, name, verbose, label):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.ext = client.ExtensionsV1beta1Api()
        self.apps = client.AppsV1Api()
        self.namespace = namespace
        self.name = name
        self.verbose = verbose
        self.selector = "%s=%s" %(label, self.name)


    def getPodInfo(self):    
        podinfo = self.v1.list_namespaced_pod(self.namespace, label_selector=self.selector)
        return podinfo

  
    def getSvcInfo(self):
        svcinfo = self.v1.list_namespaced_service(self.namespace, label_selector=self.selector)
        return svcinfo


    def getIngressInfo(self):
        ingressinfo = self.ext.list_namespaced_ingress(self.namespace, label_selector=self.selector)
        return ingressinfo


    def getIngressRouteInfo(self):
        # get details of Traefik ingress route
        pass

    def getController(self):
        # check each controller type and stop once found
       
        if self.apps.list_namespaced_deployment(self.namespace, label_selector=self.selector).items != []:
            controller = "Deployment"
        elif self.apps.list_namespaced_daemon_set(self.namespace, label_selector=self.selector).items != []:
            controller = "DaemonSet"
        elif self.apps.list_namespaced_stateful_set(self.namespace, label_selector=self.selector).items != []:
            controller = "StatefulSet"
        else:
            controller = "Unknown"
            print(f"{err}Could not find controller for {self.name}{rst}")
        return controller


    def getPodEnvs(self, data):
        values = []
        for i in data.items:
            for c in i.spec.containers:
                for e in c.env:
                    v = self.getPodEnvValue(e)
                    if v != "__False__":
                        values.append(v)
        return set(values)

    def getPodEnvValue(self, env):
        if env.value_from:
            if env.value_from.config_map_key_ref:
                return env.value_from.config_map_key_ref.name
            elif env.value_from.secret_key_ref:
                return env.value_from.secret_key_ref
            else:
                return "__False__"
        else:
            return "__False__"

    def getPodMountedValues(self, data):
        configs = []
        secrets = []
        pvc = []
        host = []
        for i in data.items:
            for v in i.spec.volumes:
                if v.secret:
                    secrets.append(v.secret.secret_name)
                elif v.config_map:
                    configs.append(v.config_map.name)
                elif v.persistent_volume_claim:
                    pvc.append(v.persistent_volume_claim.claim_name)
                elif v.host_path:
                    host.append(v.host_path.path)
                    
        return set(configs), set(secrets), set(pvc), set(host)

    """
    def getAppSecrets(self, data):
        # get the configured secrets from the pod
        secrets = []
        secrets.append(self.getPodEnvs(data))
        secrets.append(self.getPodMountedValues(data))
        return secrets
        

    def getAppConfigs(self, data):
        # get the configured ConfigMaps from the pod
        configs = []
        configs.append(self.getPodEnvs(data))
        configs.append(self.getPodMountedValues(data))
        return configs
    """

    def getContainers(self, data):
        # list all the conatiners in a pod
        # runs in verbose mode
        containers = []
        for i in data.items:
            for c in i.spec.containers:
                containers.append(c.name)
        return containers


    def main(self):
        """Entry into the appviewer class

        Gathers information about the app and shows to the user

        returns data <dict>
        """
        pods = []
        services = []
        ingress = []
        storage = {}
        storage["pvc"] = []
        storage["hostPath"] = []
        secrets = []
        configs = []
        nodes = []
        labels = {}
        annotations = {}
        containers = []

        podinfo = self.getPodInfo()
        # get the details pod information
        for p in podinfo.items:
            pods.append(p.metadata.name)
            nodes.append(p.spec.node_name)
            for l in p.metadata.labels:
                labels[l] = p.metadata.labels[l]
            for a in p.metadata.annotations:
                annotations[a] = p.metadata.annotations[a]
        # get the network based resources
        for s in self.getSvcInfo().items:
            services.append(s.metadata.name)
        for i in self.getIngressInfo().items:
            ingress.append(i.metadata.name)
        # get configs, secrets and mounts from podinfo
        config, secret, pvc, host = self.getPodMountedValues(podinfo)
        for c in config:
            configs.append(c)
        for s in secret:
            secrets.append(s) 
        for p in pvc:
            storage["pvc"].append(p)
        for h in host:
            storage["hostPath"].append(h)
        # get the list of containers in a pod           
        for c in self.getContainers(podinfo):
            containers.append(c)

        data = {
            "app": self.name,
            "controller": self.getController(),
            "pods": pods,
            "services": services,
            "ingress": ingress,
            "storage": storage,
            "secrets": secrets,
            "configs": configs,
            "nodes": set(nodes)
        }

        if self.verbose:
            data["namespace"] = self.namespace
            data["containers"] = set(containers)
            data["labels"] = labels
            data["annotations"] = annotations
        return data

if __name__ == "__main__":
    version = "%(prog)s " + __version__
    parser = argparse.ArgumentParser(allow_abbrev=True, 
                                    description="Show all resources related to an app")
    parser.add_argument("--version", "-v",
                        action="version",
                        version=version)
    parser.add_argument("--namespace", "-n",
                        dest="ns",
                        type=str,
                        default="default",
                        help="Set namespace",
                        )
    parser.add_argument("--debug", "-d",
                        action="store_true",
                        dest="debug",
                        help="Display debug information",
                        )
    parser.add_argument("--verbose", "-a",
                        action="store_true",
                        dest="verbose",
                        help="Show detailed information of resources",
                        )
    parser.add_argument("--output", "-o",
                        dest="output",
                        type=str,
                        default="table",
                        help="Format plugin output (Raw, JSON, Table, Pretty)")
    parser.add_argument("--label", "-l",
                        dest="label",
                        type=str,
                        default="app",
                        help="Define label to search against. Default to 'app'")
    parser.add_argument("name")
    parser.set_defaults(allns=False)

    args = parser.parse_args()

    app = appInfo(namespace=args.ns,
                  name=args.name,
                  verbose=args.verbose,
                  label=args.label
                )
    data = app.main()

    out = outputHandler(data=data, 
                        output=args.output,
                        verbose=args.verbose
                    )
    out.main()

