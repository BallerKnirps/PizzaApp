<template>
    <v-card class="mx-auto my-2" max-width="600">
        <v-card-title>
            <div class="d-flex justify-space-between">
                <div>
                    <h3 class="text-h6">{{ from }}</h3>
                    <p class="text-subtitle-1">{{ createdDateTime }}</p>
                </div>
            </div>
        </v-card-title>
        <v-card-text v-html="message" style="padding:20px"></v-card-text>
    </v-card>

</template>
<script setup>
import { computed } from 'vue';

const props = defineProps({
    messageData: {
        type: Object,
        required: true
    }
})

const body = computed(() => {
    return props.messageData.body
})

const message = computed(() => {
    return formatMessage(props.messageData.body.content) || 'No content available'
})

const from = computed(() => {
    return props.messageData.from.user.displayName || 'Unknown User'
})

const form_id = computed(() => {
    return props.messageData.from.user.id
})

const createdDateTime = computed(() => {
    return new Date(props.messageData.createdDateTime).toLocaleTimeString()
})

function formatMessage(message) {
    return message
    var span = document.createElement('span');
    span.innerHTML = message;
    return span.textContent || span.innerText;
    
}



</script>