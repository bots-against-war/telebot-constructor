<script lang="ts">
  import { Stack, TextInput } from "@svelteuidev/core";
  import type { ContentBlock, MenuBlock } from "../../../api/types";
  import NodeModalControls from "../../components/NodeModalControls.svelte";
  import { Button } from "@svelteuidev/core";
  import { writable } from "svelte/store";

  export let config: MenuBlock;
  export let onConfigUpdate: (newConfig: MenuBlock) => any;

  function updateConfig() {
    onConfigUpdate(config);
  }

  let fields = writable([{ id: 1, text: "" }]);

  const addField = () => {
    fields.update(n => {
      const newId = n[n.length - 1].id + 1;
      return [...n, { id: newId, text: "" }];
    });
  };

  const deleteField = id => {
    fields.update(n => n.filter(item => item.id !== id));
  };

</script>

<div>
  <h3>Меню</h3>
  <Stack>
    <div slot="content">
      {#each $fields as field (field.id)}
        <div class="field">
          <TextInput bind:value={field.text} placeholder="Type here..." />
          {#if field.id !== 1}
            <Button on:click={() => deleteField(field.id)} text="Delete" />
          {/if}
        </div>
      {/each}
      {#if $fields.length < 5}
        <Button on:click={addField} text="Add Field" />
      {/if}
    </div>
  </Stack>
  <NodeModalControls on:save={updateConfig} />
</div>

<style>
</style>
