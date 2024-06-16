<template>
  <div class="loading">
    <div class="loading_middle">
      <NuxtImg
        src="https://img.icons8.com/?size=100&id=gGiE9u2aJPFz&format=png&color=000000"
        width="100"
        class="spinner"
      />
      <h2>Загрузка...</h2>
    </div>
  </div>
</template>

<style scoped lang="scss">
.loading {
  width: 100vw;
  height: calc(100vh - 82.5px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading_middle {
  font-family: Rosatom;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
