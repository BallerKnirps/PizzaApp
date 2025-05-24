<template>
    <div class="slideshow">
        <div class="history-graph">
            <HistoryGraph :messages="messages"></HistoryGraph>
        </div>
        <transition name="slide-fade" mode="out-in">
            <Slide :person="currentUser" :history="currentUserHistory" v-if="currentUser" :key="currentUser.id" />
        </transition>
    </div>
</template>

<script setup>
import Slide from '@/components/Slide.vue';
import HistoryGraph from '@/components/HistoryGraph.vue';
import { ref, onMounted } from 'vue';


const props = defineProps({
    messages: {
        type: Array,
        default: () => []
    },
    driverHistory: {
        type: Array,
        default: () => []
    }
});

const users = ref([]);
const currentUser = ref(null);
const currentUserHistory = ref([]);

const currentIndex = ref(0);


function calculateNextSlide(user) {
    // Calculate the next slide index based on the current user
    const userIndex = users.value.findIndex(u => u.id === user.id);
    if (userIndex !== -1) {
        currentIndex.value = userIndex;
    } else {
        currentIndex.value = 0; // Reset to first user if not found
    }
}


onMounted(() => {
    // Initialize users from messages, unique by user.id
    console.log('Initializing users from messages...');
    const userMap = new Map();
    props.messages.forEach(message => {
        if (message.from && message.from.user && message.from.user.id) {
            userMap.set(message.from.user.id, message.from.user);
        }
    });
    users.value = Array.from(userMap.values());

    // Set the first user as current
    if (users.value.length > 0) {
        currentUser.value = users.value[0];
        currentUserHistory.value = props.messages.filter(
            history => history.from.user.id === currentUser.value.id
        );
    }

    // make a slideshow of users
    setInterval(() => {
        if (users.value.length > 0) {
            currentIndex.value = (currentIndex.value + 1) % users.value.length;
            currentUser.value = users.value[currentIndex.value];
            currentUserHistory.value = props.messages.filter(
                history => history.from.user.id === currentUser.value.id
            );
        }
    }, 5000); // Change slide every 5 seconds
});



</script>

<style scoped>
/* Slide from right to left */
.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.6s cubic-bezier(.55,0,.1,1);
  width: 100%;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(100%);
}
.slide-fade-enter-to {
  opacity: 1;
  transform: translateX(0);
}
.slide-fade-leave-from {
  opacity: 1;
  transform: translateX(0);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-100%);
}
.slideshow {
  position: relative;
  min-height: 200px; /* adjust as needed */
}
.history-graph {
  top: 0;
  left: 0;
  width: 100%;
  height: 45%;
}
</style>