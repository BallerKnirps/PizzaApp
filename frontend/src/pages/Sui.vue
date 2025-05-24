<template >
    <div class="sui">
        <div class="messages">
            <Messages :messages="messages"></Messages>
        </div>
        <div class="drivers">
            <Drivers :driverHistory="driverHistory"></Drivers>
            <Drivers :driverHistory="driverHistory" :messages="messages"></Drivers>
        </div>
        <div class="menu-viewer">
          <ReportSlide :messages="messageHistory" :driverHistory="driverHistory" v-if="messageHistory.length"></ReportSlide>
        </div>
    </div>
</template>
<script setup>
import Messages from '@/components/Messages.vue';
import Drivers from '@/components/Drivers.vue';
import messagesData from '@/data/messages.json';
import ReportSlide from '@/components/ReportSlide.vue';
import { ref } from 'vue';
import { onMounted, onBeforeUnmount } from 'vue';


const messages = ref([])
const socket = ref(null);
const driverHistory = ref([]);
const messageHistory = ref([]);


onMounted(() => {
    connectWebSocket();
    fetchDriverHistory()
        .then(data => {
            driverHistory.value = data;
            console.log('Driver history:', driverHistory.value);
            
        })
        .catch(error => {
            console.error('Error fetching driver history:', error);
        });
    fetchHistoryMessages().then(data => {
        messageHistory.value = data;
    }).catch(error => {
        console.error('Error fetching message history:', error);
    });
})

const connectWebSocket = () => {
  if (socket.value) {
    socket.value.close(); // Close any existing connection
  }

  // Connect to WebSocket server (adjust URL as needed)
  socket.value = new WebSocket('ws://localhost:8000/ws/teams');

  // Handle incoming messages
  socket.value.onmessage = (event) => {
    const res = JSON.parse(event.data); // Assuming the message is in JSON format
    console.log('Received message:', res);
    messages.value = res.sort((a, b) => {
      return new Date(a.createdDateTime) - new Date(b.createdDateTime);
    });
  };

  // Handle WebSocket errors
  socket.value.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  // Handle WebSocket closure
  socket.value.onclose = () => {
    console.log('WebSocket connection closed');
  };
};


function fetchDriverHistory() {
  // Fetch driver history from the server or use a static JSON file
  // For now, we'll use a static JSON file
  return fetch('http://localhost:8000/driver-history', 
    {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            // Add any other headers you need
        }
    }
  ) // Adjust the URL as needed
    .then(response => response.json())
    .then(data => {
      return data;
    })
    .catch(error => {
      console.error('Error fetching driver history:', error);
      return [];
    });
}


async function fetchHistoryMessages() {
  // Fetch message history from the server or use a static JSON file
  // For now, we'll use a static JSON file
  const resp = await fetch('http://localhost:8000/messages', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      // Add any other headers you need
    }
  });
  if (!resp.ok) {
    throw new Error('Network response was not ok');
  }
  const data = await resp.json();
  messageHistory.value = data;
  console.log('Message history:', messageHistory.value);
  return data;
}


// Cleanup WebSocket connection before the component is unmounted
onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close();
  }
});

</script>
<style scoped>
.sui {
    padding: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    width: 100%;
    height: 100svh;
}

.messages {
    grid-row: 1 / span 1;
    grid-column: 1 / span 1;
    padding: 20px;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    overflow: scroll;
    overflow-x: hidden;
}

.drivers {
    grid-row: 2 / span 1;
    grid-column: 1 / span 1;
    padding: 20px;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

.menu-viewer {
    grid-row: 1 / span 2;
    grid-column: 2 / span 1;
    padding: 20px;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    overflow: hidden;
    overflow-x: hidden;
}
</style>