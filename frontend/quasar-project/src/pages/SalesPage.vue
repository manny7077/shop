<template>
  <div class="q-pa-md">
    <q-toolbar class="text-primary q-pb-md">
      <q-btn flat round dense icon="shopping_cart" />
      <q-toolbar-title>
        <span class="text-weight-bold">Record a Sale</span>
      </q-toolbar-title>
      <q-space />
    </q-toolbar>

    <q-card class="q-pa-md">
      <q-card-section>
        <div class="text-h6 text-primary">Record a Sale</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="recordSale">
          <div v-for="(item, index) in sales" :key="index" class="q-mb-md q-gutter-sm row">
            <q-select
              v-model="item.product"
              label="Select Product"
              :options="products.map(p => ({ label: p.name, value: p.id }))"
              option-value="value"
              option-label="label"
              emit-value
              map-options
              outlined
              class="col-5"
              @update:model-value="updateStock(index, item.product)"
            />
            <q-btn icon="delete" color="negative" flat @click="removeItem(index)" class="col-1" />
          </div>

          <q-card-actions align="right">
            <q-btn label="Add Another Item" color="secondary" @click="addItem" />
            <q-btn type="submit" label="Complete Sale" color="primary" />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { api } from "src/boot/axios";

defineProps({
  product: Object,  // Existing prop for selected product
  products: Array   // New prop for product list
});

const sales = ref([{ product: null, quantity_sold: 1 }]);
const selectedProductStock = ref([]);
const shopId = ref(null);
const shopName = ref(null);

const fetchSalesSummary = async () => {
  try {
    const salesCountsResponse = await api.get("sales/counts/");
    // Handle sales counts if needed in SaleDialog
  } catch (error) {
    console.error("Error fetching sales summary:", error);
  }
};

onMounted(async () => {
  try {
    const shopInfoRes = await api.get("shop/info/");
    shopId.value = shopInfoRes.data.shop_id;
    shopName.value = shopInfoRes.data.shop_name;
  } catch (error) {
    console.error("Error fetching shop info:", error.response?.data?.error || error.message);
  }
  fetchSalesSummary();  // Keep this if you need sales summary here
});

const updateStock = (index, productId) => {
  const product = products.value.find(p => p.id === productId);
  selectedProductStock.value[index] = product ? product.quantity : null;
};

const addItem = () => {
  sales.value.push({ product: null, quantity_sold: 1 });
};

const removeItem = (index) => {
  sales.value.splice(index, 1);
  selectedProductStock.value.splice(index, 1);
};

const recordSale = async () => {
  try {
    const saleData = {
      shop: shopId.value,
      sales: sales.value.map(item => ({
        product_id: item.product,
        quantity: item.quantity_sold
      }))
    };
    await api.post("sales/record/", saleData);
  } catch (error) {
    console.error(error.response?.data?.error || "Error processing sale");
  }
};
</script>

<style scoped>
.q-toolbar-title {
  font-size: 18px;
}
</style>