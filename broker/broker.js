var net = require('net');
var Lazy = require('lazy');

////////////////////////////////////////////////////////////
// CONSTANTS
////////////////////////////////////////////////////////////

var PORT = 1337;
var MAX_TOKENS = 30;

////////////////////////////////////////////////////////////

if (process.argv.length >= 3) {
  PORT = parseInt(process.argv[2]);
}

////////////////////////////////////////////////////////////
// CLASSES
////////////////////////////////////////////////////////////

var Token = function(socket, srcID) {
  this.socket = socket;
  this.srcID = srcID;
  this.acquired_time = null;
}

var TokenType = function(type, max_tokens) {
  this.type = type;
  this.q = [];
  this.max_tokens = max_tokens;
  this.used_tokens = 0;
  this.issued = {};

  // request
  this.acquire = function(socket, srcID) {
    var token = new Token(socket, srcID);
    this.q.push(token);
    console.log("Token requested for: " + srcID);
    this.process();
  }

  this.release = function(socket, srcID) {
    // check srcID
    if (this.issued.hasOwnProperty(srcID)) {
      var token = this.issued[srcID];
      delete this.issued[srcID];
      this.used_tokens--;
      socket.end("RELEASED\n");
      console.log("Token released for: " + srcID);
    } else {
      socket.end("ERROR: srcID not found\n");
      console.log("srcID " + srcID + " not found");
    }
    this.process();
  }

  // actual acquire
  this.process = function() {
    while (this.used_tokens < this.max_tokens && this.q.length > 0) {
      var token = this.q.shift();
      try {
        token.socket.end("ACQUIRED\n");
        token.socket = null; // Make available for GC
        token.acquired_time = Date.now();
        this.used_tokens++;
        this.issued[token.srcID] = token;
        console.log("Token acquired for: " + token.srcID);
      } catch (e) {
        console.log("Cannot write to socket for src: " + token.srcID);
      }
    }
  }
};

var Broker = function(types) {
  // types is a string array of types that
  // you want to initialize broker with.

  this.manager = {};

  for (var i=0; i<types.length; i++) {
    this.manager[types[i]] = new TokenType(types[i], MAX_TOKENS);
  }

  this.acquire = function(socket, type, srcID) {
    if (this.manager.hasOwnProperty(type)) {
      this.manager[type].acquire(socket, srcID);
    } else {
      console.log("Unknown type: " + type);
      socket.end("ERROR: Unknown type\n");
    }
  }

  this.release = function(socket, type, srcID) {
    if (this.manager.hasOwnProperty(type)) {
      this.manager[type].release(socket, srcID);
    } else {
      console.log("Unknown type: " + type);
      socket.end("ERROR: Unknown type\n");
    }
  }
}

////////////////////////////////////////////////////////////
// SERVER
////////////////////////////////////////////////////////////

var broker = new Broker(['net']);

var server = net.createServer(function(socket) {

  var inputParser = new Lazy(socket).lines.forEach(function(msg) {
    var data = msg.toString();
    // console.log("RECV > " + data);
    var tokens = data.split("|");
    var cmd = tokens[0];

    if (cmd == 'acquire') {
      var type = tokens[1];
      var srcID = tokens[2];
      broker.acquire(socket, type, srcID);
    } else if (cmd == 'release') {
      var type = tokens[1];
      var srcID = tokens[2];
      broker.release(socket, type, srcID);
    } else {
      scoket.end("ERROR: Cannot parse line\n");
      console.log("Cannot parse line: " + data);
    }
  });

  // socket.on('end', function() {
  // });

  socket.on('data', function(data) {
    inputParser.emit(data.toString());
  });
});

server.listen(PORT);
