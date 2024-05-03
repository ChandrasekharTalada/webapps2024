# import threading
# from django.core.management import execute_from_command_line
# from thrift.transport import TSocket, TTransport
# from thrift.protocol import TBinaryProtocol
# from thrift.server import TServer

# # Django application
# def run_django_app():
#     execute_from_command_line(['manage.py', 'runserver', '8000'])

# class TimestampCollectorHandler(TimestampService.Iface):
#     def collectTimestamp(self, transaction_id, timestamp):
#         print(f"Received timestamp {timestamp} for transaction {transaction_id}")

# # Thrift server
# def start_thrift_server():
#     handler = TimestampCollectorHandler()
#     processor = TimestampService.Processor(handler)
#     transport = TSocket.TServerSocket(port=10000)
#     tfactory = TTransport.TBufferedTransportFactory()
#     pfactory = TBinaryProtocol.TBinaryProtocolFactory()
#     server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
#     print("Starting Thrift server...")
#     server.serve()

# def run_thrift_server():
#     thrift_server_thread = threading.Thread(target=start_thrift_server)
#     thrift_server_thread.start()

# if __name__ == '__main__':
#     django_app_thread = threading.Thread(target=run_django_app)
#     django_app_thread.start()

#     run_thrift_server()





