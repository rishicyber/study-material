# Kubernetes & Helm: Deep Dive Reference

> A comprehensive ~1000-line guide covering architecture, core concepts, networking, storage, security, scaling, and Helm charts with real commands.

---

## Table of Contents

1. [Kubernetes Architecture](#1-kubernetes-architecture)
2. [Cluster Setup & kubectl](#2-cluster-setup--kubectl)
3. [Pods](#3-pods)
4. [Controllers: Deployments, ReplicaSets, StatefulSets, DaemonSets](#4-controllers)
5. [Services & Networking](#5-services--networking)
6. [Ingress & Gateway API](#6-ingress--gateway-api)
7. [ConfigMaps & Secrets](#7-configmaps--secrets)
8. [Volumes & Persistent Storage](#8-volumes--persistent-storage)
9. [Resource Management & QoS](#9-resource-management--qos)
10. [Namespaces, RBAC & Security](#10-namespaces-rbac--security)
11. [Health Probes & Lifecycle Hooks](#11-health-probes--lifecycle-hooks)
12. [Horizontal & Vertical Pod Autoscaling](#12-autoscaling)
13. [Jobs & CronJobs](#13-jobs--cronjobs)
14. [Network Policies](#14-network-policies)
15. [Taints, Tolerations & Affinity](#15-taints-tolerations--affinity)
16. [Helm Charts — Deep Dive](#16-helm-charts--deep-dive)
17. [Helm — Advanced Patterns](#17-helm--advanced-patterns)
18. [Observability Cheatsheet](#18-observability-cheatsheet)
19. [Troubleshooting Runbook](#19-troubleshooting-runbook)

---

## 1. Kubernetes Architecture

### Control Plane Components

| Component | Role |
|---|---|
| `kube-apiserver` | REST gateway — every kubectl call hits this |
| `etcd` | Distributed key-value store; source of truth for all cluster state |
| `kube-scheduler` | Watches for unscheduled pods and assigns them to nodes |
| `kube-controller-manager` | Runs reconciliation loops (Deployment, Node, Endpoint controllers…) |
| `cloud-controller-manager` | Integrates with cloud provider APIs (LBs, routes, volumes) |

### Node Components

| Component | Role |
|---|---|
| `kubelet` | Agent on every node; talks to API server, manages containers |
| `kube-proxy` | Maintains iptables/ipvs rules for Service virtual IPs |
| Container Runtime | containerd, CRI-O — runs the actual containers |

### Reconciliation Loop (the heart of K8s)

```
Desired State (etcd)  ──►  Controller  ──►  Actual State
        ▲                       │
        └───── diff & act ──────┘
```

Everything in Kubernetes is a control loop: observe → diff → act.

---

## 2. Cluster Setup & kubectl

### Local Clusters

```bash
# kind (Kubernetes IN Docker)
kind create cluster --name dev --config kind-config.yaml
kind get clusters
kind delete cluster --name dev

# minikube
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube dashboard
minikube stop

# k3d (k3s in Docker)
k3d cluster create mycluster --agents 3
```

### kubeconfig Management

```bash
# View current context
kubectl config current-context
kubectl config get-contexts

# Switch context
kubectl config use-context prod-cluster

# Merge multiple kubeconfigs
KUBECONFIG=~/.kube/config:~/other-cluster.yaml kubectl config view --flatten > ~/.kube/merged

# Set a namespace permanently for a context
kubectl config set-context --current --namespace=my-app
```

### Essential kubectl Flags

```bash
-n <namespace>          # Target namespace
--all-namespaces / -A   # Across all namespaces
-o wide                 # Extra columns (node, IP)
-o yaml                 # Full YAML output
-o json | jq '.spec'    # JSON + pipe to jq
--watch / -w            # Stream updates
--dry-run=client -o yaml  # Preview without applying
--field-selector status.phase=Running
--selector app=web,env=prod   # Label selectors
```

---

## 3. Pods

A Pod is the smallest deployable unit — one or more containers sharing a network namespace and volumes.

### Minimal Pod Manifest

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
    tier: frontend
spec:
  containers:
    - name: nginx
      image: nginx:1.25-alpine
      ports:
        - containerPort: 80
      env:
        - name: ENV
          value: "production"
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "250m"
          memory: "256Mi"
```

### Multi-Container Pod Patterns

```yaml
# Sidecar pattern — logging agent alongside main app
spec:
  containers:
    - name: app
      image: my-app:latest
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
    - name: log-shipper
      image: fluent/fluent-bit:latest
      volumeMounts:
        - name: logs
          mountPath: /var/log/app
  volumes:
    - name: logs
      emptyDir: {}
```

### Init Containers

```yaml
spec:
  initContainers:
    - name: wait-for-db
      image: busybox
      command: ['sh', '-c', 'until nc -z db-service 5432; do sleep 2; done']
  containers:
    - name: app
      image: my-app:latest
```

### Pod Commands

```bash
kubectl run debug --image=busybox --rm -it --restart=Never -- sh
kubectl exec -it nginx-pod -- bash
kubectl exec -it nginx-pod -c log-shipper -- sh   # specific container
kubectl logs nginx-pod --tail=100 -f
kubectl logs nginx-pod -c log-shipper --previous  # crashed container logs
kubectl cp nginx-pod:/var/log/app.log ./app.log
kubectl port-forward pod/nginx-pod 8080:80
kubectl describe pod nginx-pod
kubectl delete pod nginx-pod --grace-period=0 --force
```

---

## 4. Controllers

### Deployment

Manages ReplicaSets → manages Pods. Supports rolling updates and rollbacks.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Extra pods during update
      maxUnavailable: 0  # Zero-downtime
  template:
    metadata:
      labels:
        app: web-app
        version: "2.1.0"
    spec:
      containers:
        - name: web
          image: my-app:2.1.0
          imagePullPolicy: IfNotPresent
```

```bash
# Deployment operations
kubectl apply -f deployment.yaml
kubectl rollout status deployment/web-app
kubectl rollout history deployment/web-app
kubectl rollout undo deployment/web-app
kubectl rollout undo deployment/web-app --to-revision=3
kubectl set image deployment/web-app web=my-app:2.2.0
kubectl scale deployment/web-app --replicas=10
kubectl rollout pause deployment/web-app   # canary gate
kubectl rollout resume deployment/web-app
```

### StatefulSet

For stateful workloads (databases, message queues). Provides:
- Stable, predictable pod names (`pod-0`, `pod-1`, `pod-2`)
- Ordered startup and shutdown
- Stable network identity via Headless Service
- Per-pod PersistentVolumeClaims

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          env:
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 20Gi
```

```bash
kubectl get statefulset postgres
kubectl scale statefulset postgres --replicas=5
# StatefulSets scale one pod at a time (ordered)
```

### DaemonSet

Runs exactly one pod on every (or selected) node. Use cases: log collectors, monitoring agents, CNI plugins.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      tolerations:
        - operator: Exists  # Run on ALL nodes including control-plane
      containers:
        - name: node-exporter
          image: prom/node-exporter:latest
          ports:
            - containerPort: 9100
              hostPort: 9100
```

---

## 5. Services & Networking

### Service Types

```yaml
# ClusterIP (default) — internal only
apiVersion: v1
kind: Service
metadata:
  name: web-svc
spec:
  type: ClusterIP
  selector:
    app: web-app
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
```

```yaml
# NodePort — accessible on every node's IP at <NodePort>
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080   # 30000-32767 range
```

```yaml
# LoadBalancer — provisions cloud LB
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: 8443
  loadBalancerSourceRanges:
    - "10.0.0.0/8"
```

```yaml
# Headless — no VIP, returns pod IPs directly (for StatefulSets)
spec:
  clusterIP: None
  selector:
    app: postgres
```

```yaml
# ExternalName — DNS CNAME alias
spec:
  type: ExternalName
  externalName: rds.us-east-1.amazonaws.com
```

### Service Commands

```bash
kubectl get svc -A
kubectl describe svc web-svc
kubectl get endpoints web-svc          # see which pods are backing it
kubectl expose deployment web-app --port=80 --target-port=8080
kubectl port-forward svc/web-svc 8080:80
```

### DNS in Kubernetes

Every Service gets a DNS record:
```
<service>.<namespace>.svc.cluster.local
```

For StatefulSet pods:
```
<pod-name>.<service>.<namespace>.svc.cluster.local
postgres-0.postgres-headless.default.svc.cluster.local
```

---

## 6. Ingress & Gateway API

### Ingress (classic)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app.example.com
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-svc
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-svc
                port:
                  number: 80
```

```bash
kubectl get ingress -A
kubectl describe ingress app-ingress
```

### Gateway API (modern replacement)

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: app-route
spec:
  parentRefs:
    - name: main-gateway
  hostnames:
    - "app.example.com"
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /api
      backendRefs:
        - name: api-svc
          port: 80
```

---

## 7. ConfigMaps & Secrets

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  config.yaml: |
    database:
      host: postgres-headless
      port: 5432
    cache:
      ttl: 300
```

```bash
kubectl create configmap app-config --from-file=config.yaml
kubectl create configmap env-config --from-literal=LOG_LEVEL=info --from-literal=ENV=prod
kubectl get configmap app-config -o yaml
kubectl edit configmap app-config
```

### Consuming ConfigMaps

```yaml
spec:
  containers:
    - name: app
      image: my-app:latest
      # Option 1: individual env vars
      env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
      # Option 2: inject all keys as env vars
      envFrom:
        - configMapRef:
            name: app-config
      # Option 3: mount as files
      volumeMounts:
        - name: config-vol
          mountPath: /etc/app
  volumes:
    - name: config-vol
      configMap:
        name: app-config
```

### Secrets

```bash
# Create secrets
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password='S3cr3t!'

kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass

kubectl create secret tls app-tls \
  --cert=tls.crt \
  --key=tls.key

# Decode a secret
kubectl get secret db-secret -o jsonpath='{.data.password}' | base64 --decode
```

```yaml
# Secret manifest (values are base64-encoded)
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=
  password: UzNjcjN0IQ==
```

> **Important**: Secrets are base64-encoded, not encrypted at rest by default. Use external secret managers (Vault, AWS Secrets Manager) with External Secrets Operator in production.

---

## 8. Volumes & Persistent Storage

### Volume Types

```yaml
# emptyDir — ephemeral, lives with the pod
volumes:
  - name: cache
    emptyDir:
      sizeLimit: 1Gi

# hostPath — mounts node filesystem (avoid in prod)
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: Socket

# configMap / secret (shown above)

# projected — combine multiple sources
  - name: combined
    projected:
      sources:
        - configMap:
            name: app-config
        - secret:
            name: db-secret
```

### PersistentVolume & PersistentVolumeClaim

```yaml
# PersistentVolume (admin creates)
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-fast-001
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteOnce
  reclaimPolicy: Retain
  storageClassName: fast-ssd
  hostPath:
    path: /mnt/data/pv-001

---
# PersistentVolumeClaim (developer requests)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 20Gi
```

### StorageClass (Dynamic Provisioning)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

```bash
kubectl get pv,pvc -A
kubectl describe pvc app-data
kubectl get sc   # storage classes
```

### Access Modes

| Mode | Abbreviation | Description |
|---|---|---|
| ReadWriteOnce | RWO | One node can mount read/write |
| ReadOnlyMany | ROX | Many nodes read-only |
| ReadWriteMany | RWX | Many nodes read/write (NFS, EFS) |
| ReadWriteOncePod | RWOP | Single pod only (K8s 1.22+) |

---

## 9. Resource Management & QoS

### Requests vs Limits

- **Request**: what the scheduler uses for placement; guaranteed to the container
- **Limit**: hard cap; CPU is throttled, memory OOMKilled if exceeded

```yaml
resources:
  requests:
    cpu: "250m"      # 0.25 vCPU
    memory: "256Mi"
  limits:
    cpu: "1"         # 1 vCPU
    memory: "512Mi"
```

### QoS Classes

| Class | Condition | Eviction Priority |
|---|---|---|
| Guaranteed | requests == limits for all containers | Last |
| Burstable | requests < limits | Middle |
| BestEffort | No requests or limits set | First |

### LimitRange (namespace defaults)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "4"
        memory: "4Gi"
```

### ResourceQuota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
    services: "10"
    persistentvolumeclaims: "20"
```

```bash
kubectl describe resourcequota -n team-a
kubectl describe limitrange -n production
```

---

## 10. Namespaces, RBAC & Security

### Namespaces

```bash
kubectl create namespace staging
kubectl get ns
kubectl delete ns staging  # deletes everything inside!
```

### RBAC

```yaml
# Role (namespace-scoped)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "update", "patch"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: production
subjects:
  - kind: User
    name: jane
    apiGroup: rbac.authorization.k8s.io
  - kind: ServiceAccount
    name: ci-bot
    namespace: ci
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# ClusterRole — cluster-wide
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
```

```bash
# Check permissions
kubectl auth can-i create pods --as=jane -n production
kubectl auth can-i '*' '*'   # am I cluster-admin?

# Inspect RBAC
kubectl get rolebindings,clusterrolebindings -A
kubectl describe clusterrole cluster-admin
```

### ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/app-role  # IRSA
automountServiceAccountToken: false  # disable unless needed
```

### Pod Security

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
          add: ["NET_BIND_SERVICE"]
```

---

## 11. Health Probes & Lifecycle Hooks

### Probe Types

```yaml
containers:
  - name: app
    image: my-app:latest

    # Startup probe — gates liveness/readiness until app is ready
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10  # Allow 5 min for slow starts

    # Liveness — restart if unhealthy
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 15
      timeoutSeconds: 5
      failureThreshold: 3

    # Readiness — remove from Service endpoints if not ready
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      successThreshold: 1
      failureThreshold: 3
```

### Probe Methods

```yaml
# HTTP GET
httpGet:
  path: /health
  port: 8080
  httpHeaders:
    - name: Authorization
      value: Bearer token123

# TCP socket
tcpSocket:
  port: 5432

# Exec command
exec:
  command:
    - /bin/sh
    - -c
    - "redis-cli ping | grep PONG"

# gRPC (1.24+)
grpc:
  port: 9090
  service: "liveness"
```

### Lifecycle Hooks

```yaml
lifecycle:
  postStart:
    exec:
      command: ["/bin/sh", "-c", "echo started > /tmp/started"]
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 5 && nginx -s quit"]
    # Or HTTP:
    # httpGet:
    #   path: /shutdown
    #   port: 8080
```

> **Graceful shutdown**: set `terminationGracePeriodSeconds` (default 30s) high enough for preStop + drain to complete.

---

## 12. Autoscaling

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Resource
      resource:
        name: memory
        target:
          type: AverageValue
          averageValue: 200Mi
    # Custom metric (requires adapter)
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
```

```bash
kubectl autoscale deployment web-app --cpu-percent=60 --min=2 --max=20
kubectl get hpa
kubectl describe hpa web-hpa
```

### Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Auto"   # Off | Initial | Recreate | Auto
  resourcePolicy:
    containerPolicies:
      - containerName: web
        minAllowed:
          cpu: 50m
          memory: 64Mi
        maxAllowed:
          cpu: 2
          memory: 2Gi
```

### KEDA (Kubernetes Event-Driven Autoscaling)

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: queue-scaler
spec:
  scaleTargetRef:
    name: worker-deployment
  minReplicaCount: 0       # Scale to zero!
  maxReplicaCount: 50
  triggers:
    - type: aws-sqs-queue
      metadata:
        queueURL: https://sqs.us-east-1.amazonaws.com/123456/jobs
        queueLength: "10"
        awsRegion: us-east-1
```

---

## 13. Jobs & CronJobs

### Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  parallelism: 3          # Run 3 pods simultaneously
  completions: 9          # Total successful completions needed
  backoffLimit: 4         # Retry failures
  activeDeadlineSeconds: 600
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: OnFailure   # Never | OnFailure
      containers:
        - name: migrator
          image: my-app:latest
          command: ["python", "manage.py", "migrate"]
```

```bash
kubectl get jobs
kubectl logs job/db-migration
kubectl wait --for=condition=complete job/db-migration --timeout=120s
```

### CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"       # 2 AM daily (UTC)
  timeZone: "America/New_York" # K8s 1.27+
  concurrencyPolicy: Forbid    # Allow | Forbid | Replace
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  startingDeadlineSeconds: 300
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: reporter
              image: reporter:latest
```

```bash
kubectl get cronjob
kubectl create job --from=cronjob/nightly-report manual-run-001  # trigger manually
```

---

## 14. Network Policies

By default all pods can talk to all pods. NetworkPolicy restricts this.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-netpol
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
    - Egress

  ingress:
    # Allow from frontend pods only
    - from:
        - podSelector:
            matchLabels:
              app: frontend
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 8080

  egress:
    # Allow to database
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    # Allow DNS
    - ports:
        - protocol: UDP
          port: 53
```

```bash
kubectl get netpol -n production
kubectl describe netpol api-netpol -n production
```

> **Note**: NetworkPolicy requires a CNI that supports it (Calico, Cilium, Weave). Not all CNIs enforce policies.

---

## 15. Taints, Tolerations & Affinity

### Taints & Tolerations

```bash
# Add taint to node
kubectl taint nodes node1 dedicated=gpu:NoSchedule
kubectl taint nodes node1 dedicated=gpu:NoExecute
kubectl taint nodes node1 dedicated=gpu:PreferNoSchedule

# Remove taint
kubectl taint nodes node1 dedicated=gpu:NoSchedule-
```

```yaml
# Tolerate the taint
spec:
  tolerations:
    - key: "dedicated"
      operator: "Equal"
      value: "gpu"
      effect: "NoSchedule"
    # Tolerate any taint (use carefully)
    - operator: "Exists"
```

### Node Affinity

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values: ["us-east-1a", "us-east-1b"]
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 80
          preference:
            matchExpressions:
              - key: node.kubernetes.io/instance-type
                operator: In
                values: ["m5.xlarge"]
```

### Pod Affinity & Anti-Affinity

```yaml
spec:
  affinity:
    # Spread replicas across nodes (anti-affinity)
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values: ["web-app"]
          topologyKey: kubernetes.io/hostname
    # Co-locate with cache pods
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                app: redis
            topologyKey: kubernetes.io/hostname
```

### Topology Spread Constraints

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: web-app
```

---

## 16. Helm Charts — Deep Dive

Helm is the package manager for Kubernetes. A **Chart** is a collection of files that describe a related set of Kubernetes resources.

### Chart Structure

```
my-app/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── values-prod.yaml    # Environment overrides
├── .helmignore
├── charts/             # Chart dependencies
├── crds/               # Custom Resource Definitions
└── templates/
    ├── _helpers.tpl    # Named templates (partials)
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── hpa.yaml
    ├── serviceaccount.yaml
    ├── NOTES.txt       # Post-install notes
    └── tests/
        └── test-connection.yaml
```

### Chart.yaml

```yaml
apiVersion: v2
name: my-app
description: A production-grade web application chart
type: application   # or "library"
version: 1.4.2      # Chart version (SemVer)
appVersion: "2.1.0" # App version (informational)
kubeVersion: ">=1.25.0"

keywords:
  - web
  - api

maintainers:
  - name: Platform Team
    email: platform@company.com

dependencies:
  - name: postgresql
    version: "13.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

### values.yaml

```yaml
# Global settings
global:
  imageRegistry: ""
  imagePullSecrets: []

# Application
replicaCount: 2

image:
  repository: my-company/my-app
  tag: ""           # Defaults to Chart.appVersion
  pullPolicy: IfNotPresent

serviceAccount:
  create: true
  name: ""
  annotations: {}

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 60

env:
  LOG_LEVEL: info
  APP_ENV: production

postgresql:
  enabled: true
  auth:
    database: myapp
    username: myapp

redis:
  enabled: false
```

### _helpers.tpl (Named Templates)

```
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
ServiceAccount name
*/}}
{{- define "my-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "my-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "my-app.serviceAccountName" . }}
      {{- with .Values.global.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ include "my-app.fullname" . }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
          readinessProbe:
            httpGet:
              path: /ready
              port: http
```

### templates/ingress.yaml (conditional)

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "my-app.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

---

## 17. Helm — Advanced Patterns

### Core Helm Commands

```bash
# Repository management
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm repo list
helm search repo bitnami/postgresql --versions

# Install & upgrade
helm install my-release ./my-app -f values-prod.yaml
helm install my-release bitnami/postgresql \
  --set auth.postgresPassword=secret \
  --namespace databases \
  --create-namespace

helm upgrade my-release ./my-app -f values-prod.yaml
helm upgrade --install my-release ./my-app   # idempotent

# Dry run & debug
helm install my-release ./my-app --dry-run --debug
helm template my-release ./my-app -f values-prod.yaml  # render locally

# Inspect
helm list -A
helm status my-release
helm get values my-release           # user-supplied values
helm get values my-release --all     # merged values
helm get manifest my-release         # rendered manifests
helm history my-release

# Rollback
helm rollback my-release 2           # roll back to revision 2
helm rollback my-release 0           # roll back to previous

# Uninstall
helm uninstall my-release
helm uninstall my-release --keep-history  # keep history for rollback
```

### Dependency Management

```bash
helm dependency update ./my-app   # download charts/ from Chart.yaml deps
helm dependency build ./my-app    # build from Chart.lock
helm dependency list ./my-app
```

### Helm Hooks

```yaml
# Pre-install job (e.g., database migration)
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ .Release.Name }}-migrate"
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"        # lower = earlier
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["python", "manage.py", "migrate"]
```

Hook types: `pre-install`, `post-install`, `pre-upgrade`, `post-upgrade`, `pre-delete`, `post-delete`, `pre-rollback`, `post-rollback`, `test`

### Helm Tests

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test"
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox
      command: ['wget', '--spider', 'http://{{ include "my-app.fullname" . }}:{{ .Values.service.port }}/healthz']
```

```bash
helm test my-release
helm test my-release --logs
```

### Helm Secrets & External Values

```bash
# Using helm-secrets plugin (with sops)
helm plugin install https://github.com/jkroepke/helm-secrets
helm secrets upgrade my-release ./my-app \
  -f values.yaml \
  -f secrets://secrets.enc.yaml

# Multiple values files (later files override earlier)
helm upgrade my-release ./my-app \
  -f values.yaml \
  -f values-prod.yaml \
  -f overrides.yaml \
  --set image.tag=abc123
```

### Helm Chart Museum (Private Registry)

```bash
# Push chart to OCI registry (Helm 3.8+)
helm package ./my-app
helm push my-app-1.4.2.tgz oci://registry.example.com/charts
helm install my-release oci://registry.example.com/charts/my-app --version 1.4.2
```

### Library Charts (Shared Templates)

```yaml
# Chart.yaml
type: library  # Cannot be installed directly

# Used in other charts
dependencies:
  - name: common
    version: "2.x.x"
    repository: https://charts.bitnami.com/bitnami
```

```
# Use library template in consumer chart
{{- include "common.deployment" (list . "my-app.deployment") -}}
```

### values.schema.json (Validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema",
  "type": "object",
  "required": ["image"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" }
      }
    }
  }
}
```

---

## 18. Observability Cheatsheet

### Metrics with Prometheus + Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prom-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --set grafana.adminPassword=secret \
  --set prometheus.prometheusSpec.retention=30d

kubectl port-forward -n monitoring svc/kube-prom-stack-grafana 3000:80
kubectl port-forward -n monitoring svc/kube-prom-stack-prometheus 9090:9090
```

### Useful kubectl Commands for Observability

```bash
# Real-time resource usage
kubectl top nodes
kubectl top pods -A --sort-by=memory
kubectl top pods -n production --containers

# Events (sorted by time)
kubectl get events -n production --sort-by='.lastTimestamp'
kubectl get events --field-selector type=Warning -A

# Node conditions
kubectl get nodes -o custom-columns=\
'NAME:.metadata.name,STATUS:.status.conditions[-1].type,READY:.status.conditions[-1].status'

# Pod disruption
kubectl get pdb -A  # PodDisruptionBudgets

# Watch rollout across namespace
kubectl get pods -n production -w

# Resource utilization summary
kubectl describe node <node-name> | grep -A 20 "Allocated resources"
```

### Logging with Loki

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm upgrade --install loki grafana/loki-stack \
  -n monitoring \
  --set promtail.enabled=true \
  --set grafana.enabled=false  # use existing Grafana
```

---

## 19. Troubleshooting Runbook

### Pod Won't Start

```bash
kubectl get pods -n <ns>                    # check STATUS and RESTARTS
kubectl describe pod <pod> -n <ns>          # check Events section
kubectl logs <pod> -n <ns>                  # current logs
kubectl logs <pod> -n <ns> --previous       # crashed container logs
kubectl logs <pod> -n <ns> -c <container>   # specific container

# Common STATUS values and meanings:
# Pending         → scheduling issue (resources, affinity, PVC)
# ImagePullBackOff → image not found or no pull secret
# CrashLoopBackOff → container crashing repeatedly
# OOMKilled       → memory limit exceeded
# Evicted         → node memory/disk pressure
# Terminating     → stuck on deletion (finalizers?)
```

### Debugging with Ephemeral Containers

```bash
# Inject debug container into running pod (K8s 1.23+)
kubectl debug -it <pod> --image=busybox --target=<container>

# Copy pod with different image for debugging
kubectl debug <pod> -it --copy-to=debug-pod --image=ubuntu --share-processes

# Node debugging
kubectl debug node/<node-name> -it --image=ubuntu
```

### Service Not Reachable

```bash
# 1. Check service exists and has endpoints
kubectl get svc,endpoints <svc-name> -n <ns>

# 2. Verify selector matches pod labels
kubectl get svc <svc-name> -o jsonpath='{.spec.selector}'
kubectl get pods --show-labels -n <ns>

# 3. Test DNS from within cluster
kubectl run dns-test --image=busybox --rm -it --restart=Never -- \
  nslookup <svc-name>.<ns>.svc.cluster.local

# 4. Test connectivity
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  curl -v http://<svc-name>.<ns>.svc.cluster.local

# 5. Check NetworkPolicy isn't blocking
kubectl get netpol -n <ns>
```

### Node Issues

```bash
kubectl get nodes
kubectl describe node <node>
kubectl cordon <node>                  # stop scheduling new pods
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
kubectl uncordon <node>                # re-enable scheduling

# Force delete stuck terminating pod
kubectl delete pod <pod> -n <ns> --force --grace-period=0

# Remove stuck finalizers
kubectl patch pod <pod> -n <ns> -p '{"metadata":{"finalizers":[]}}' --type=merge
```

### Helm Troubleshooting

```bash
# Release stuck in pending-install or failed
helm list -A --all                     # show all states
helm status my-release -n <ns>
helm rollback my-release -n <ns>

# Delete failed release
helm uninstall my-release -n <ns>

# Check rendered templates for bugs
helm template my-release ./my-app --debug 2>&1 | head -100

# Lint chart
helm lint ./my-app -f values-prod.yaml

# Compare installed vs local chart
helm get manifest my-release -n <ns> > installed.yaml
helm template my-release ./my-app -f values-prod.yaml > local.yaml
diff installed.yaml local.yaml
```

### Common Gotchas

| Problem | Likely Cause | Fix |
|---|---|---|
| Pods Pending | Insufficient node resources | `kubectl describe pod` → check events |
| ImagePullBackOff | Wrong image tag or missing imagePullSecret | Check image name; add pull secret |
| CrashLoopBackOff | App error or bad config | `kubectl logs --previous` |
| Service no endpoints | Label mismatch | Compare `svc.spec.selector` vs pod labels |
| PVC stuck Pending | No matching StorageClass or no available PV | `kubectl describe pvc` |
| HPA not scaling | Metrics server not installed | `kubectl top pods` should work |
| Helm hook timeout | Job taking too long | Increase `--timeout` flag |
| OOMKilled | Memory limit too low | Increase `resources.limits.memory` |

---

## Quick Reference Card

```bash
# The big three — check these first in any incident
kubectl get pods -A | grep -v Running
kubectl get events -A --sort-by='.lastTimestamp' | tail -30
kubectl top nodes

# Fast context switching
alias kns='kubectl config set-context --current --namespace'
alias kctx='kubectl config use-context'

# Port-forward anything quickly
kubectl port-forward svc/grafana -n monitoring 3000:80 &
kubectl port-forward svc/prometheus -n monitoring 9090:9090 &

# Force-restart a deployment (rolling)
kubectl rollout restart deployment/<name>

# Get all resources in a namespace
kubectl get all -n production

# Decode any secret quickly
kubectl get secret <name> -o go-template='{{range $k,$v := .data}}{{$k}}={{$v | base64decode}}{{"\n"}}{{end}}'

# Watch pod startup
kubectl get pods -w -n production

# Helm — upgrade or install in one line (CI/CD)
helm upgrade --install --atomic --timeout 5m \
  --namespace production --create-namespace \
  -f values.yaml -f values-prod.yaml \
  --set image.tag=${GIT_SHA} \
  my-release ./chart
```

---

*End of Kubernetes & Helm Deep Dive — ~1000 lines*
