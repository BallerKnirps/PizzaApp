<template>
  <v-card v-if="potentialDrivers.length && !chosenDriver" class="mt-6">
    <v-card-title>Potential Drivers</v-card-title>
    <v-card-text>
      <v-chip-group column>
        <v-chip v-for="driver in potentialDrivers" :key="driver" class="ma-1">{{ driver.displayName }}</v-chip>
      </v-chip-group>
    </v-card-text>
    <v-card-actions>
      <v-btn color="success" @click="startRollAnimation" :loading="loadingRoll">
        Roll for Driver!
      </v-btn>
    </v-card-actions>
  </v-card>

  <v-card v-if="showRandomizer" class="mt-8 text-center pa-4" elevation="10">
    <v-card-title class="justify-center headline">
      <v-icon large left>mdi-steering</v-icon>
      Wer fährt heute?
      <v-icon large right>mdi-pizza</v-icon>
    </v-card-title>
    <v-card-text>
      <div class="randomizer-display d-flex align-center justify-center">
        <span :class="{'spinning-text': isRolling, 'final-text': !isRolling}">
          <!-- Show rolling name or winner -->
          <template v-if="isRolling">
            {{ displayedDriverName?.displayName || '...' }}
          </template>
          <v-alert v-else-if="chosenDriver && !isRolling" type="success" class="mt-4 text-center">
            <h3 class="headline">🎉 The chosen one is: {{ chosenDriver.displayName }}! 🎉</h3>
            <p class="mt-2">{{  subMessage }}</p>
          </v-alert>
          <template v-else>
            ...
          </template>
        </span>
      </div>
    </v-card-text>
    <v-card-actions v-if="!isRolling" class="justify-center">
      <v-btn color="blue darken-1" text @click="postDriver(chosenDriver)">Passt?</v-btn>
    </v-card-actions>
  </v-card>

  </template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import subMessagesData from '@/data/messages.json'; // Assuming you have a JSON file with message data
import axios from 'axios';

const props = defineProps({
  driverHistory: {
    type: Array,
    default: () => []
  },
  messages: {
    type: Array,
    default: () => []
  },
});


// --- Reactive State ---
// ... (teamsChannelId, messages, etc. - these are for gathering the *pool* of drivers) ...
const driverHistory = ref(props.driverHistory); 
const potentialDrivers = computed(() => {
  // Map messages to user objects, then filter out duplicates by user id (or displayName if id is not available)
  const users = props.messages.map(message => message.from.user);
  const seen = new Set();
  return users.filter(user => {
    const key = user.id || user.displayName;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
});
const chosenDriver = ref(null);    // The final selected driver
const loadingRoll = ref(false);    // Indicates if the roll animation is in progress
const showRandomizer = ref(false); // Controls visibility of the randomizer card
const isRolling = ref(false);      // Controls the spinning animation effect
const displayedDriverName = ref(null); // The name currently shown in the randomizer display
const subMessage = ref(''); // Additional message to display with the chosen driver

// ... (historyHeaders, driverHistory, loadingHistory) ...

// --- Methods ---

// ... (fetchTeamsMessages, extractPotentialDrivers, fetchDriverHistory - these populate potentialDrivers) ...

const calculateWeightedDriver = () => {
  if (potentialDrivers.length === 0) {
    // This check is crucial for the driver selection
    alert('No potential drivers found. Fetch messages first!');
    return null;
  }
  const DrivenTimes = driverHistory.value.reduce((acc, driver) => {
    acc[driver.DriverName] = (acc[driver.DriverName] || 0) + 1;
    return acc;
  }, {});

    const totalDrives = Object.values(DrivenTimes).reduce((acc, count) => acc + count, 0);
    console.log(potentialDrivers)
    const weightedDrivers = potentialDrivers.value.map(driver => {
        const driverCount = DrivenTimes[driver] || 0;
        const weight = (totalDrives - driverCount) / totalDrives; // Higher weight for less driven drivers
        return { name: driver, weight };
        });

    // Normalize weights
    const totalWeight = weightedDrivers.reduce((acc, driver) => acc + driver.weight, 0);

    const normalizedDrivers = weightedDrivers.map(driver => ({
        name: driver.name,
        weight: driver.weight / totalWeight
    }));
    // Select a driver based on the normalized weights
    const randomValue = Math.random();
    let cumulativeWeight = 0;
    let selectedDriver = null;
    for (const driver of normalizedDrivers) {
        cumulativeWeight += driver.weight;
        if (randomValue <= cumulativeWeight) {
            selectedDriver = driver.name;
            break;
        }
    }
    // If no driver is selected, fallback to a random choice
    if (!selectedDriver) {
        const randomIndex = Math.floor(Math.random() * potentialDrivers.value.length);
        selectedDriver = potentialDrivers.value[randomIndex];
    }
    // Return the selected driver
    return selectedDriver;
};

const startRollAnimation = async () => {
  if (potentialDrivers.value.length === 0) {
    alert('No potential drivers found. Fetch messages first!');
    return;
  }

  // --- Animation Setup ---
  loadingRoll.value = true;
  showRandomizer.value = true;
  isRolling.value = true;
  chosenDriver.value = null; // Clear previous winner

  let rollCount = 0;
  const totalRolls = 30; // Number of times to cycle names
  const intervalDuration = 80; // Milliseconds between name changes

  // Crucially, the *final* driver is determined here using the weighted logic
  // BEFORE the animation starts, so it can land on the correct one.
  const finalDriver = calculateWeightedDriver();

  const rollInterval = setInterval(() => {
    rollCount++;
    // ... (logic to make the animation appear to spin and slow down) ...

    if (rollCount <= totalRolls) {
      // During the "spin", display a random driver from the `potentialDrivers` array
      const randomIndex = Math.floor(Math.random() * potentialDrivers.value.length);
      displayedDriverName.value = potentialDrivers.value[randomIndex];
    } else {
      // When animation finishes, set the display to the actual chosen driver
      displayedDriverName.value = finalDriver;
      clearInterval(rollInterval);
      isRolling.value = false; // Stop the spinning effect
      chosenDriver.value = finalDriver; // Set the official chosen driver

      loadingRoll.value = false;

      // --- Post-Roll Logic ---
      // set a random message from the subMessagesData
      const randomIndex = Math.floor(Math.random() * subMessagesData.length);
      subMessage.value = subMessagesData[randomIndex];
    }
  }, intervalDuration);
};

const postDriver = async (driver) => {
  fetch('http://localhost:8000/driver-history', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ driver }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log('Driver stored successfully:', data);
    })
    .catch((error) => {
      console.error('Error storing driver:', error);
    });
};

const resetRoll = () => {
  // Allows user to reset the display for another roll
  chosenDriver.value = null;
  showRandomizer.value = false;
  displayedDriverName.value = null;
};
</script>

<style scoped>
/* ... (CSS for .randomizer-display, .spinning-text, .final-text, @keyframes) ... */
</style>