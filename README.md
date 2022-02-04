# Apps

The Apps plugin will show Kubernetes resources associated with a pod, service or pod controller (daemonset, deployment etc.).

This should give a quick view of all resources associated with your application to help with troubleshooting. This will include

* PVCs and PVs
* Secrets and ConfigMaps (mounted and referenced)
* Services
* Ingress and IngressRoutes
* All containers in a pod
* Other mounts
* Scheduled node
* Labels and annotaions

The plugin filters resources on a sepcified label. This defaults to 'app' and can be configured using `--label`. This command will get all resources for an app labelled with `mylabel=myapp`.

```
kubectl s90-podinspect -n default -l mylabel myapp
```

## Installation

**Written using Python 3.8.5, will require python >=3.6 to run**

* From Source

Get the repo and move the file into place

```
git clone https://github.com/schizoid90/s90-podinspect.git
mkdir -r ~/.krew/store/s90-resources/0.1.0/
mv kubectl-s90-resources/src/* ~/.krew/store/s90-resources/0.1.0/
chmod +x ~/.krew/store/s90-resources/0.1.0/
```

## How to use

```
usage: kubectl-s90-podinspect [-h] [--version] [--namespace NS] [--debug] [--verbose]
                      [--output OUTPUT] [--label LABEL]
                      name

Show all resources related to an app

positional arguments:
  name
                                                                                                                                                                optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --namespace NS, -n NS
                        Set namespace
  --debug, -d           Display debug information
  --verbose, -a         Show detailed information of resources
  --output OUTPUT, -o OUTPUT
                        Format plugin output (Raw, JSON, Table, Pretty)
  --label LABEL, -l LABEL
                        Define label to search against. Default to 'app'
```

Diplayed in table, pretty, JSON or raw (Python dict) format

* Table (Default)

```
$ kubectl s90-podinspect myapp
+-------------+----------------------------------------------+-----------------------------+-----------------------------+---------+---------+------------+-------------------------------+
|     App     |                     Pods                     |           Service           |           Ingress           | Storage | Secrets | ConfigMaps |             Nodes             |
+-------------+----------------------------------------------+-----------------------------+-----------------------------+---------+---------+------------+-------------------------------+
| myapp       | ['myapp-7dcdfc495f-vfpd7']                   | ['myapp']                   | ['myapp']                   | {mounts}|{secrets}|{ConfigMaps}| {'k8s-prod-n3.dr-foster.lan'} |
+-------------+----------------------------------------------+-----------------------------+-----------------------------+---------+---------+------------+-------------------------------+ 
```

* Pretty

```
App: {application}
Namespace: {namespace}
Pods:
        {pods}
Linked Services:
        {services}
Linked Ingress resources:
        {ingress}
Mounted Storage:
        {mounts}
Linked Secrets:
        {secrets}
Linked ConfigMaps:
        {configMaps}
Running on Nodes:
        {nodes}
Labels:
        {labels}
Annotations:
        {annotations}
```
