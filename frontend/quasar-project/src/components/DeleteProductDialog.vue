<template>
  <q-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)">
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="warning" color="negative" text-color="white" />
        <span class="q-ml-sm">Are you sure you want to delete this product?</span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" @click="$emit('update:modelValue', false)" />
        <q-btn flat label="Delete" color="negative" @click="confirmDelete" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar';

const props = defineProps({
  modelValue: Boolean, // v-model binding for dialog visibility
  productId: Number // ID of the product to be deleted
});

const emit = defineEmits(['update:modelValue', 'refresh']);

const $q = useQuasar();

const confirmDelete = async () => {
  try {
    await api.delete(`products/${props.productId}/`);
    $q.notify({ message: 'Product deleted successfully', color: 'positive' });
    emit('refresh'); // Refresh the product list
  } catch (error) {
    $q.notify({ message: 'Error deleting product', color: 'negative' });
  }
  emit('update:modelValue', false); // Close the dialog
};
</script>
