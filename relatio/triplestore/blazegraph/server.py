
import os
import signal
import subprocess

URL_BLAZEGRAPH = "http://localhost:9999/bigdata/sparql"


def add_move_to_path(cmd:  str, 
                     path: str) -> str:
    """
    Add command to move to path, to cmd
    """
    return f"cd {path} && " + cmd


def init_server(path: str = "") -> None:
    """ 
    Initialize Blazegraph server with local file
    """
    cmd = "java -cp blazegraph.jar com.bigdata.rdf.store.DataLoader p.properties triplestore.nq"
    if path:
        cmd = add_move_to_path(cmd, path)
    subprocess.run(cmd, shell=True)


def launch_server(path: str = "") -> subprocess.Popen:
    """ 
    Launch Blazegraph server 
    """
    cmd = "java -server -Xmx4g -jar blazegraph.jar"
    if path:
        cmd = add_move_to_path(cmd, path)
    return subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)


def stop_server(bg: subprocess.Popen) -> None:
    """ 
    Kill Blazegraph server 
    """
    bg = os.getpgid(bg.pid)
    os.killpg(bg, signal.SIGTERM)
