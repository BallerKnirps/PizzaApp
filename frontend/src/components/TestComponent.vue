<template>
  <v-container>
    <h1 class="mb-4">Teams Pizza Chat Messages</h1>
    <v-text-field
      v-model="teamsChannelId"
      label="Teams Channel ID"
      outlined
      dense
      placeholder="e.g., 19:abcdef..."
    ></v-text-field>
    <v-btn color="primary" @click="fetchTeamsMessages" :loading="loadingMessages" class="mb-4">
      Fetch Messages
    </v-btn>

    <v-card v-if="messages.length">
      <v-card-title>Messages from Today</v-card-title>
      <v-card-text>
        <v-list dense>
          <v-list-item v-for="message in messages" :key="message.id">
            <v-list-item-content>
              <v-list-item-title>
                <strong>{{ message.from.user.displayName || 'Unknown User' }}:</strong>
                {{ message.body.content }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ new Date(message.createdDateTime).toLocaleTimeString() }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <v-card v-if="potentialDrivers.length" class="mt-6">
      <v-card-title>Potential Drivers</v-card-title>
      <v-card-text>
        <v-chip-group column>
          <v-chip v-for="driver in potentialDrivers" :key="driver" class="ma-1">{{ driver }}</v-chip>
        </v-chip-group>
      </v-card-text>
      <v-card-actions>
        <v-btn color="success" @click="rollForDriver" :loading="loadingRoll">
          Roll for Driver
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-alert v-if="chosenDriver" type="info" class="mt-4">
      <h3 class="headline">The chosen driver is: {{ chosenDriver }}!</h3>
    </v-alert>

    <v-card class="mt-6">
      <v-card-title>Driver History</v-card-title>
      <v-card-text>
        <v-data-table
          :headers="historyHeaders"
          :items="driverHistory"
          :loading="loadingHistory"
          class="elevation-1"
        ></v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import axios from 'axios'; // For making API calls

export default {
  data: () => ({
    teamsChannelId: '', // Replace with your actual channel ID or make it configurable
    messages: [],
    loadingMessages: false,
    potentialDrivers: [],
    driverHistory: [],
    loadingHistory: false,
    chosenDriver: null,
    loadingRoll: false,
    historyHeaders: [
      { text: 'Driver Name', value: 'DriverName' },
      { text: 'Date Driven', value: 'DateDriven' },
    ],
  }),
  async created() {
    await this.fetchDriverHistory();
  },
  methods: {
    async fetchTeamsMessages() {
      this.loadingMessages = true;
      this.messages = [];
      this.potentialDrivers = [];
      try {
        const response = await axios.get(`http://localhost:3000/api/teams/messages/${this.teamsChannelId}`);
        this.messages = response.data;
        this.extractPotentialDrivers();
      } catch (error) {
        console.error('Error fetching Teams messages:', error);
        alert('Failed to fetch Teams messages. Check console for details.');
      } finally {
        this.loadingMessages = false;
      }
    },
    extractPotentialDrivers() {
      const uniqueDrivers = new Set();
      this.messages.forEach(message => {
        if (message.from && message.from.user && message.from.user.displayName) {
          uniqueDrivers.add(message.from.user.displayName);
        }
      });
      this.potentialDrivers = Array.from(uniqueDrivers);
    },
    async fetchDriverHistory() {
      this.loadingHistory = true;
      try {
        const response = await axios.get('http://localhost:3000/api/sharepoint/drivers');
        this.driverHistory = response.data.map(item => ({
            DriverName: item.DriverName || item.Title, // Use DriverName if available, else Title
            DateDriven: new Date(item.DateDriven).toLocaleDateString(), // Format date
        }));
      } catch (error) {
        console.error('Error fetching driver history:', error);
        alert('Failed to fetch driver history.');
      } finally {
        this.loadingHistory = false;
      }
    },
    async rollForDriver() {
      if (this.potentialDrivers.length === 0) {
        alert('No potential drivers found. Fetch messages first!');
        return;
      }

      this.loadingRoll = true;
      this.chosenDriver = null;

      // Calculate weighted probabilities
      const driverCounts = {};
      this.driverHistory.forEach(entry => {
        driverCounts[entry.DriverName] = (driverCounts[entry.DriverName] || 0) + 1;
      });

      let totalWeight = 0;
      const weightedDrivers = [];

      for (const driver of this.potentialDrivers) {
        const timesDriven = driverCounts[driver] || 0;
        // The less a person has driven, the higher their weight
        // You can adjust this weighting formula. Here, 1 / (timesDriven + 1)
        // If timesDriven is 0, weight is 1. If 1, weight is 0.5. If 2, weight is 0.33.
        const weight = 1 / (timesDriven + 1);
        totalWeight += weight;
        weightedDrivers.push({ driver, weight });
      }

      // Random selection based on weights
      let randomNumber = Math.random() * totalWeight;
      for (const { driver, weight } of weightedDrivers) {
        if (randomNumber < weight) {
          this.chosenDriver = driver;
          break;
        }
        randomNumber -= weight;
      }

      // Store the chosen driver in SharePoint
      if (this.chosenDriver) {
        try {
          await axios.post('http://localhost:3000/api/sharepoint/drivers', {
            driverName: this.chosenDriver,
            dateDriven: new Date().toISOString().split('T')[0], // YYYY-MM-DD
          });
          alert(`${this.chosenDriver} has been chosen as the driver and recorded!`);
          await this.fetchDriverHistory(); // Refresh history
        } catch (error) {
          console.error('Error storing driver in SharePoint:', error);
          alert('Failed to store driver in SharePoint.');
        }
      }
      this.loadingRoll = false;
    },
  },
};
</script>