<template>
    <div class="info">
        <h1>{{ person.displayName }}</h1>
        <p>Bestellungen: {{ totalOrders }}</p>
        <p>Durchschnittliche Bestellzeit: {{ avgOrderTime }}</p>
        <p>Letzte Bestellungen am: {{ lastOrderTime }}</p>
        <p>Geld Verbraucht: muss noch implementiert werden</p>
    </div>
</template>
<script setup>
import { computed } from 'vue';

const props = defineProps({
    person: {
        type: Object,
        default: () => ({ displayName: 'Unknown Driver' })
    },
    history: {
        type: Array,
        default: () => []
    }
});



const totalOrders = computed(() => {
    // Calculate the total number of orders for the person -> only 1 per day
    const uniqueDays = new Set();
    props.history.forEach(order => {
        const orderDate = new Date(order.createdDateTime);
        uniqueDays.add(orderDate.toISOString().split('T')[0]); // Add only the date part
    });
    return uniqueDays.size;
});

const avgOrderTime = computed(() => {
    // get avg of first message a day
    if (props.history.length === 0) return 'N/A';
    const dailyOrders = {};
    props.history.forEach(order => {
        const orderDate = new Date(order.createdDateTime).toISOString().split('T')[0];
        if (!dailyOrders[orderDate]) {
            dailyOrders[orderDate] = []
        } 
        dailyOrders[orderDate].push(order.createdDateTime);
    });
    const totalTime = Object.values(dailyOrders).reduce((acc, times) => {
        return acc + new Date(Math.min(...times.map(iso_string => new Date(iso_string)))).getTime();
    }, 0);
    const avgTime = totalTime / Object.keys(dailyOrders).length;
    return new Date(avgTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
});

const lastOrderTime = computed(() => {
    if (props.history.length === 0) return 'N/A';
    const lastOrder = props.history[props.history.length - 1];
    return new Date(lastOrder.createdDateTime).toLocaleString();
});

</script>

<style scoped>
.info {
  background: #2a2a2a;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1), 0 1.5px 6px rgba(0,0,0,1);
  padding: 2rem 2.5rem;
  margin: 2rem auto;
  max-width: 400px;
  min-width: 260px;
  text-align: center;
  transition: box-shadow 0.3s;
}

.info:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,1), 0 3px 12px rgba(0,0,0,1);
}

.info h1 {
  font-size: 2rem;
  margin-bottom: 1.2rem;
  color: #50a1f2;
  letter-spacing: 1px;
}

.info p {
  font-size: 1.1rem;
  margin: 0.7rem 0;
  color: #DDD;
}

.info p:last-child {
  margin-bottom: 0;
  color: #DDD;
  font-style: italic;
}
</style>