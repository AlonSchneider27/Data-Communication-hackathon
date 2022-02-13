import socket
import struct
import threading
import time
import concurrent.futures
import random
import multiprocessing
import scapy.all

global port
port = 2102


def broadcast(UDP_s):
    message = struct.pack('Ibh', 0xabcddcba, 0x2, port)
    UDP_s.sendto(message, ("<broadcast>", 13117))  # 172.99.255.255

def send_offers_by_thread(UDP_s):
    threading.Timer(1.0, send_offers_by_thread, args=[UDP_s]).start()
    broadcast(UDP_s)

def run_game_on_client(client_socket):  # run_game_on_client
    start_t = time.time()
    ans = None
    client_socket.settimeout(10)
    try:
        message = client_socket.recv(1024)
        ans = message.decode("utf-8")
    except:
        pass
    return (time.time() - start_t, ans)


def play_best_game_ever():
    play = True
    while play:
        # -------------LET-THE-GAME-BEGIN-------------#
        players = []
        SERVER_IP = scapy.all.get_if_addr("eth1")

        # PORT_NUM = port
        print(f"Server started,listening on IP address {SERVER_IP}")

        UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        UDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        UDP.bind((str(SERVER_IP), 13117))

        offers_threading = multiprocessing.Process(target=send_offers_by_thread, args=(UDP,))
        offers_threading.start()

        global TCP
        TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCP.bind(('', port))
        TCP.listen(2)
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            while True:

                (client_socket, address_1) = TCP.accept()
                client_name = client_socket.recv(1024).decode("utf-8")
                players.append((client_socket, client_name))

                (client_socket, address_2) = TCP.accept()
                client_name = client_socket.recv(1024).decode("utf-8")
                players.append((client_socket, client_name))

                time.sleep(10)
                # Generate equations
                x = list(range(10))
                a = random.choice(x)
                b = random.choice(list(range(9 - a + 1)))
                question = str(a) + ' + ' + str(b)
                answer = str(a + b)
                start_message = bytes(
                    "Welcome to Quick Maths.\n" + f"Player 1: {players[0][1]}\n" + f"Player 2: {players[1][1]}\n" + "==\n" + "Please answer the following question as fast as you can:\n" + f"How much is {question}?",
                    "utf-8")

                try:  # if clients disconect during the waiting 10 sec, an error raise, the try saves the day and the server restarts the game
                    for client, client_name in players:
                        client.sendall(start_message)
                except:
                    for client, client_name in players:
                        client.close()
                    UDP.close()
                    TCP.close()
                    print("A CLIENT HAS BEEN DISCCONECTED BEFORE THE GAME STARTED")
                    break

                client_game1 = pool.submit(run_game_on_client, players[0][0])
                client_game2 = pool.submit(run_game_on_client, players[1][0])

                results = []

                game1_result = client_game1.result()

                game2_result = client_game2.result()

                results.append((players[0][0], players[0][1], game1_result))
                results.append((players[1][0], players[1][1], game2_result))

                print(results)
                if results[0][-1][-1] == '' or results[1][-1][-1] == '':  # restart server if a client disconects before the game has started

                    for client, client_name in players:
                        try:
                            client.close()
                        except:
                            continue
                    UDP.close()
                    TCP.close()
                    print("A CLIENT HAS BEEN DISCONECTED DURING THE GAME")
                    break

                if results[0][-1][-1] is None and results[1][-1][-1] is None:
                    draw_message = bytes("Game over!\n" + f"The correct answer was {answer}!\n\n" + "It's a draw!",
                                         "utf-8")
                    for client, client_name in players:
                        client.sendall(draw_message)
                        client.close()
                    UDP.close()
                    TCP.close()

                    break

                results = sorted(results, key=lambda x: x[-1][0], reverse=False)
                print(results)

                first = results[0]
                last = results[1]
                try:
                    valid_ans = isinstance(int(first[-1][-1]), int)
                except:
                    valid_ans = False
                winner = None
                print(valid_ans)
                if valid_ans and first[-1][-1] == answer:
                    winner = first
                else:
                    winner = last

                summary = bytes(
                    "Game over!\n" + f"The correct answer was {answer}!\n\n" + f"Congratulations to the winner: {winner[1]}",
                    "utf-8")

                for client, client_name in players:
                    client.sendall(summary)
                    client.close()
                UDP.close()
                TCP.close()
                break


if __name__ == '__main__':
    play_best_game_ever()

