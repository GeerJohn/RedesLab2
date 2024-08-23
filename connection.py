# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

from base64 import b64encode
from constants import *
import logging
import os


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.s = socket
        self.buffer = ''
        self.connected = True
        self.dir = directory

    def _recv(self, timeout=None):
        """
        Recibe datos y acumula en el buffer interno.

        Para uso privado del servidor.
        """
        self.s.settimeout(timeout)
        data = self.s.recv(4096).decode("ascii")
        self.buffer += data

        if len(data) == 0:
            logging.info("El cliente interrumpió la conexión.")
            self.connected = False

    def send(self, message, timeout=None):
        """
        Envía el mensaje 'message' al cliente, seguido por el terminador de
        línea del protocolo.

        Si se da un timeout, puede abortar con una excepción socket.timeout.

        También puede fallar con otras excepciones de socket.
        """
        self.s.settimeout(timeout)
        # Agregar EOL acá no hace falta, se hace en los comandos o respuestas
        # individuales
        while message:
            logging.debug("Enviando el (resto del) mensaje %s."
                          % repr(message))
            bytes_sent = self.s.send(message.encode("ascii"))
            assert bytes_sent > 0
            message = message[bytes_sent:]

    def get_file_listing(self):
        buffer = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
        lista = os.listdir(self.dir)
        for element in lista:
            buffer += element + EOL
        buffer += EOL
        return buffer

    def get_metadata(self, filename):
        buffer = ""
        if not filename in os.listdir(self.dir):
            buffer = self.error_command(FILE_NOT_FOUND)
        if not buffer:
            buffer = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
            size = os.path.getsize(self.dir + os.path.sep + filename)
            buffer = buffer + str(size) + EOL
        return buffer

    def get_slice(self, filename, offset, size):
        buffer = ""
        filepath = self.dir + os.path.sep + filename
        # Probamos que ambos sean no negativos
        if offset < 0 or size < 0:
            buffer = self.error_command(INVALID_ARGUMENTS)
        else:
            if not filename in os.listdir(self.dir):
                buffer = self.error_command(FILE_NOT_FOUND)
            if not buffer and offset + size > os.path.getsize(filepath):
                buffer = self.error_command(BAD_OFFSET)
            if not buffer:
                try:
                    buffer = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
                    file = open(filepath, "rb")
                    slice = file.read()[offset:size+offset]
                    b64bytes = b64encode(slice)
                    buffer = buffer + str(b64bytes)[2:-1] + EOL
                    file.close()
                except:
                    # No seguro si debería estar esto
                    buffer = self.error_command(INTERNAL_ERROR)
        return buffer
    
    def get_suma(self, arg1, arg2):
        if arg1 < 0 or arg2 < 0:
            buffer = self.error_command(INVALID_ARGUMENTS)
        else:
            buffer = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
            result = arg1 + arg2
            buffer += str(result) + EOL
        return buffer

    def quit(self):
        buffer = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
        self.connected = False
        return (buffer)

    def error_command(self, code):
        buffer = str(code) + ' ' + error_messages[code] + EOL
        # buffer += error_details[code] + EOL
        if fatal_status(code):
            self.connected = False
        return buffer

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        timeout = None
        # Idea: Envolver en try except
        # a todo esto y si algo ocurre mandarle el error 199
        while self.connected:
            if not EOL in self.buffer:
                self._recv(timeout)
            else:
                message = ""
                # Divido en una lista la data recibida del cliente y separo el primer comando
                comando = self.buffer.split(EOL, 1)
                # Revisar si aparece \n en data fuera de un terminador \r\n
                if "\n" in comando[0]:
                    message = self.error_command(BAD_EOL)
                    self.send(message)
                else:
                    # Quitamos lo obtenido en la línea 134
                    self.buffer = self.buffer.replace(EOL.join(comando), "", 1)
                    # Divido el primer comando por si tiene argumentos
                    splitcom = comando[0].split()
                    # uso splitcom[0] para ver el primer elemento(osea el primer comando)
                    if splitcom[0] == "get_file_listing":
                        if len(splitcom) > 1:
                            # No debería recibir nada más
                            message = self.error_command(INVALID_ARGUMENTS)
                        else:
                            message = self.get_file_listing()
                    elif splitcom[0] == "get_metadata":
                        if len(splitcom) < 2 or len(splitcom) > 2:
                            # Sólo el comando o hay más de un FILENAME
                            message = self.error_command(INVALID_ARGUMENTS)
                        else:
                            # De otra forma completar
                            filename = splitcom[1]
                            message = self.get_metadata(filename)
                    elif splitcom[0] == "get_slice":
                        if len(splitcom) < 4 or len(splitcom) > 4:
                            # Por la forma del comando get_slice FILENAME OFFSET SIZE
                            message = self.error_command(INVALID_ARGUMENTS)
                        # Probamos que sean enteros
                        try:
                            offset = int(splitcom[2])
                            size = int(splitcom[3])
                        except:
                            message = self.error_command(INVALID_ARGUMENTS)
                        if not message:
                            # O tratamos de completar el pedido
                            filename = splitcom[1]
                            message = self.get_slice(filename, offset, size)
                    elif splitcom[0] == "quit":
                        if len(splitcom) > 1:
                            # No debería recibir nada más
                            message = self.error_command(INVALID_ARGUMENTS)
                        else:
                            message = self.quit()
                    elif splitcom[0] == "get_suma":
                        if len(splitcom) < 3 or len(splitcom) > 3:
                            message = self.error_command(INVALID_COMMAND)
                        try:
                            arg1 = int(splitcom[1])
                            arg2 = int(splitcom[2])
                        except:
                            message = self.error_command(INVALID_ARGUMENTS)
                        if not message: 
                            message = self.get_suma(arg1, arg2)
                    else:
                        # Un comando incorrecto no es fatal
                        message = self.error_command(INVALID_COMMAND)
                    # Mandamos la respuesta apropiada
                    self.send(message)
        print("Closing Connection")
        self.s.close()
