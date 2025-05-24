<template>
    <div>
        <ul>
            <li v-for="message in messages" :key="message.id">
                <Message :messageData="message" @delete-message="deleteMessage" />
            </li>
        </ul>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import Message from '@/components/Message.vue';


const props = defineProps({
    messages: {
        type: Array,
        required: true
    }
});

const deleteMessage = (id) => {
    messages.value = props.messages.value.filter(message => message.id !== id);
};

</script>
<style scoped>

.messages {
    padding: 20px;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100vh;
}

ul {
    list-style-type: none;
    padding: 0;
}
</style>