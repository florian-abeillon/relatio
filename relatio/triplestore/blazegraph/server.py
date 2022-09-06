
import os
import signal
import subprocess

from ..utils import format_path

URL_BLAZEGRAPH = "http://localhost:9999/bigdata/sparql"


def add_move_to_path(cmd: str, path: str) -> str:
    """
    Add command to move to path, to cmd
    """
    path = format_path(path)
    return f"cd {path} && " + cmd


def init(path: str = "") -> None:
    """ 
    Initialize Blazegraph server with local file
    """
    cmd = "java -cp blazegraph.jar com.bigdata.rdf.store.DataLoader p.properties triplestore.trig"
    if path:
        cmd = add_move_to_path(cmd, path)
    subprocess.run(cmd, shell=True)


def launch(path: str = "") -> subprocess.Popen:
    """ 
    Launch Blazegraph server 
    """
    cmd = "java -server -Xmx4g -jar blazegraph.jar"
    if path:
        cmd = add_move_to_path(cmd, path)
    return subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)


def stop(blazegraph: subprocess.Popen) -> None:
    """ 
    Kill Blazegraph server 
    """
    blazegraph = os.getpgid(blazegraph.pid)
    os.killpg(blazegraph, signal.SIGTERM)
