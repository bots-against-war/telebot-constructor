<script lang="ts">
  import { onDestroy } from "svelte";

  let wiggling = false;
  const wiggleInterval = setInterval(() => {
    wiggling = true;
    setTimeout(() => (wiggling = false), 600);
  }, 4000);
  onDestroy(() => {
    clearInterval(wiggleInterval);
  });

  let jumping = false;
  const jumpInterval = setInterval(() => {
    jumping = true;
    setTimeout(() => (jumping = false), 600);
  }, 3000);
  onDestroy(() => {
    clearInterval(jumpInterval);
  });
</script>

<div class="{jumping ? 'jump' : ''} {wiggling ? 'wiggle' : ''}">
  <slot />
</div>

<style>
  .jump {
    animation: jump 0.3s ease-out;
  }

  @keyframes jump {
    0%,
    100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-3px);
    }
  }

  .wiggle {
    animation: wiggle 0.25s ease-in-out;
  }

  @keyframes wiggle {
    0%,
    100% {
      transform: rotate(0deg);
    }
    25% {
      transform: rotate(-8deg);
    }
    75% {
      transform: rotate(8deg);
    }
  }
</style>
