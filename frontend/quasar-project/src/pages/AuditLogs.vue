<template>
    <div class="q-pa-md">
      <!-- Elevated Toolbar -->
      <q-toolbar class="bg-white text-primary shadow-1 rounded-borders q-px-md q-py-sm">
        <q-btn flat round dense icon="history" />
        <q-toolbar-title class="text-weight-bold">Audit Logs</q-toolbar-title>
        <q-space />
        <q-btn
          flat
          label="Export to Excel"
          color="green"
          icon="file_download"
          @click="exportToExcel"
          class="q-mr-md"
        />
        <q-btn
          flat
          label="Back to Inventory"
          color="primary"
          icon="arrow_back"
          @click="$router.push('/')"
        />
      </q-toolbar>
  
      <!-- Table Container -->
      <q-card-section>
        <q-table
          :rows="auditLogs"
          :columns="columns"
          row-key="id"
          :loading="loading"
          class="custom-table"
          flat
          bordered
          no-data-label="No audit logs found"
        >
          <template v-slot:loading>
            <q-inner-loading showing color="primary">
              <q-spinner-gears size="50px" color="primary" />
              <p class="text-primary q-mt-sm">Loading audit logs...</p>
            </q-inner-loading>
          </template>
        </q-table>
      </q-card-section>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useQuasar } from 'quasar';
  import { api } from 'src/boot/axios';
  import { usePermissionStore } from 'src/stores/permission';
  import { useRouter } from 'vue-router';
  import * as XLSX from 'xlsx';
  
  const $q = useQuasar();
  const permission = usePermissionStore();
  const router = useRouter();
  
  const auditLogs = ref([]);
  const loading = ref(false);
  
  const columns = [
    {
      name: 'timestamp',
      label: 'Time',
      field: 'timestamp',
      sortable: true,
      align: 'left',
      format: val => new Date(val).toLocaleString()
    },
    {
      name: 'user',
      label: 'User',
      field: 'user',
      sortable: true,
      align: 'left'
    },
    {
      name: 'activity',
      label: 'Activity',
      field: row => row.details?.description || `${row.action_display} occurred`,
      sortable: true,
      align: 'left'
    },
    {
      name: 'ip_address',
      label: 'IP Address',
      field: 'ip_address',
      sortable: true,
      align: 'left'
    }
  ];
  
  const fetchAuditLogs = async () => {
    loading.value = true;
    try {
      const response = await api.get("/audit-logs/");
      auditLogs.value = response.data;
    } catch (error) {
      $q.notify({ type: 'negative', message: 'Failed to load audit logs.' });
      console.error("Error fetching audit logs:", error);
      if (error.response?.status === 403) {
        router.push('/');
      }
    } finally {
      loading.value = false;
    }
  };
  
  const exportToExcel = () => {
    // Prepare data for Excel without the Details column
    const data = auditLogs.value.map(row => ({
      Time: new Date(row.timestamp).toLocaleString(),
      User: row.user || 'N/A',
      Activity: row.details?.description || `${row.action_display} occurred`,
      'IP Address': row.ip_address || 'N/A'
    }));
  
    // Create worksheet and workbook
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Audit Logs');
  
    // Export to file
    XLSX.writeFile(wb, `audit_logs_${new Date().toISOString().split('T')[0]}.xlsx`);
    $q.notify({ type: 'positive', message: 'Audit logs exported to Excel!' });
  };
  
  onMounted(fetchAuditLogs);
  </script>
  
  <style scoped>
  .q-toolbar-title {
    font-size: 18px;
  }
  
  .custom-table {
    border-radius: 8px;
    background-color: white;
  }
  
  .q-btn {
    transition: all 0.2s ease-in-out;
  }
  .q-btn:hover {
    transform: scale(1.05);
  }
  
  .q-card {
    border-radius: 12px;
  }
  
  .q-card-section {
    padding-top: 10px;
    padding-bottom: 10px;
  }
  </style>