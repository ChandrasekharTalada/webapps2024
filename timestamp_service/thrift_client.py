# thrift_server.py
import time
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from .gen_py import TimestampCollector

class TimestampCollectorHandler(TimestampCollector.Iface):
    def collectTimestamp(self, transaction_id, timestamp):
        print(f"Received timestamp {timestamp} for transaction {transaction_id}")

def start_thrift_server():
    handler = TimestampCollectorHandler()
    processor = TimestampCollector.Processor(handler)
    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print("Starting Thrift server...")
    server.serve()

# Start the Thrift server in a separate thread
start_thrift_server()
