# LDN6: Plug programming
We have found that communicating through an online classroom forum is time consuming and impractical. Students would like to communicate with each other reliably and in real time. There are many solutions online that would be appropriate, but none meet all of our requirements. So we have no choice but to program something of our own like real computer scientists.
You have two partial implementations (Java and Python), but they are extremely simple, as they only send simple text messages. Choose one of the programming languages and complete both programs (talk server and client) so that they will be able to send and receive structured data, for which you can use the XML, JSON format or something of your own.

- ChatServer.java
- ChatClient.java
- chatServer.py
- chatClient.py
## Requirements
- Server
    - Server must be multithreaded (already done)
    - The server must support simultaneous communication with multiple clients (already done)
    - Every public message that reaches the server is sent to all clients (already done)
    - Private messages are only sent to the recipient
        - If the addressee is not logged in to the chat server, an error message should be sent to the sender
    - Each message sent by the server to the client must be accompanied by the name of the original sender
- Client
    - The student must log in to the client with his name
    - The program connects to the chat server and sends to it all the messages that the student types via the standard STDIN input (already done)
    - Each message sent by the student to the server must be accompanied by his name and time of sending
