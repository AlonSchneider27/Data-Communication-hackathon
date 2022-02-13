# Data-Communication-hackathon
A Client Server game created during a hackathon focused on data communication. Implementing Server side and Client side using python.<br />

This is a short game that's implemented using a server and two clients. The server broadcasts UDP offers and the clients receive them and initiate a TCP connection with the server.<br />
After the clients are connceted to the server, the server generates a random simple math question and sends it to the clients.<br />
The First client that answers wins the game if it was correct - otherwise the other team wins. Incase no one answers it's a draw. <br />
The server sends the clients the game results, discconects and starts sending new offers broadcast. The clients start to listen to broadcast again as well.
