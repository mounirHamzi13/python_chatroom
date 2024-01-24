# Importation des modules nécessaires
import socket  # Module pour la gestion des sockets
import select  # Module pour la gestion des opérations d'I/O multiplexées
import pickle  # Module pour la sérialisation des objets Python

# Création du socket serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Définition de l'hôte (adresse IP) et du port d'écoute
host, port = "127.0.0.1", 9001

# Liaison du socket avec l'adresse et le port spécifiés
server.bind((host, port))

# Mise en écoute du socket
server.listen()

# Initialisation des variables
client_connected = True
socket_objs = [server]  # Liste des objets de socket à surveiller
print('Bienvenue dans le chat !')

# Boucle principale du serveur
while client_connected:
    # Utilisation de select pour surveiller les sockets en lecture
    readable_sockets, _, _ = select.select(socket_objs, [], socket_objs)
    sockets_to_remove = []  # Liste pour stocker les sockets à supprimer

    # Parcours des sockets prêts en lecture
    for socket_obj in readable_sockets:
        # Si le socket est le socket serveur, alors il y a une nouvelle connexion
        if socket_obj is server:
            client, address = server.accept()
            socket_objs.append(client)
            print(f'Nouveau participant connecté : {address}')
            message = {
                'sender' : 'system'.encode('utf-8') ,
                'message' : 'Nouveau participant connecté'.encode('utf-8')

            }
            print(len(socket_objs))
            for client_socket in socket_objs:
                    if client_socket != server and client_socket != socket_obj:
                        try:
                            if len(socket_objs)>2:
                                client_socket.send(pickle.dumps(message))
                            else : 
                                client_socket.send(pickle.dumps({'sender':'system'.encode('utf-8'),'message':'Bienvenue dans le chat !'.encode('utf-8')}))
                        except socket.error:
                            print("Erreur lors de la diffusion du message.")
        else:
            try:
                # Réception des données depuis un client
                data_received = socket_obj.recv(1024)

                # Vérification de la déconnexion du participant
                if not data_received:
                    print('Participant déconnecté')
                    sockets_to_remove.append(socket_obj)
                    continue

                # Désérialisation des données reçues
                received_object = pickle.loads(data_received)
                sender = received_object['sender'].decode('utf-8')
                message = received_object['message'].decode('utf-8')
                print(f'{sender}: {message}')

                # Diffusion du message à tous les autres participants
                for client_socket in socket_objs:
                    if client_socket != server and client_socket != socket_obj:
                        try:
                            client_socket.send(data_received)
                        except socket.error:
                            print("Erreur lors de la diffusion du message.")
            except socket.error:
                print('Participant déconnecté')
                message = {
                    'sender' : 'system'.encode('utf-8') ,
                    'message' : 'Participant déconnecté'.encode('utf-8')
                    }
                for client_socket in socket_objs:
                        if client_socket != server and client_socket != socket_obj:
                            try:
                                client_socket.send(pickle.dumps(message))
                            except socket.error:
                                print("Erreur lors de la diffusion du message.")
                sockets_to_remove.append(socket_obj)

    # Suppression des sockets déconnectés après la boucle
    for socket_to_remove in sockets_to_remove:
        socket_objs.remove(socket_to_remove)
        socket_to_remove.close()
        print(f'{len(socket_objs) - 1} participant(s) encore connecté(s)')

    # Vérification s'il n'y a plus de participants, et fermeture du serveur si nécessaire
    if len(socket_objs) - 1 == 0:
        print("Aucun participant, fermeture du serveur")
        server.close()
        break
