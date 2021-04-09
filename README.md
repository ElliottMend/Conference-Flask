# Conferencing Site

A Conferencing web application built using ReactJS, Typescript, Flask & PostgresDB. While also utilizing SocketIO (HTTP/WebSocket hybrid) to allow real time user communication as well as WebRTC for video chatting. It allows users to create rooms to talk to their friends/coworkers via text chat or video chat. Unit and Integrations tests done with pytest.


## Design Decisions
### Purpose
The goal behind building this application was to learn more about how users can interact live through the internet. While I had heard of terms such as “WebSocket’s” or “WebRTC” I hadn’t done much research into them or how they are used which is why I started working on this project and made them the focus of the project. As for the WebSocket’s, after doing some research I came across “SocketIO” which is built upon WebSocket’s and HTTP to provide a more reliable and more easily integrated product. With WebRTC I went with a similar path using the “simple-peer” library which handled the RTCPeer connections and made understanding the connections and signaling needed to connect two peers much easier.

### Frontend
For the frontend stack I went with Reactjs primarily because it’s the main stack I use and am most comfortable with as well as really enjoy using. During the process of working on this application I picked up Typescript in another project then quickly adopted it here. Despite having not used it for very long it already feels like something I can’t live without the static typing and error handling are something that I feel are a necessity.

### Backend
Unlike the frontend I decided to use a new stack, around the time of starting this project I had been working with python on some small projects (scripts & small data science projects) and decided to use that as a gateway to learn a python framework. Initially I started using Django as it seemed to be popular and pretty well liked, however I felt like I was spending more time learning the multitude of libraries rather than what the libraries were doing and because of that I switched to Flask. Flask has been great so far, I enjoy using barebones libraries being able to flesh out the design to my specific customization. As far as the database I decided to use PostgreSQL as it’s my preferred database seeing as it’s open source, very reliable and has some nice added features over other relational databases. Whilst working on this project I had discovered Redis, which has been a great tool and has made caching significantly easier and has allowed me to store sessions of both Flask and SocketIO making connections much more optimized.
