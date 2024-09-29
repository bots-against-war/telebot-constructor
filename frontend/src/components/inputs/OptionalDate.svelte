<script lang="ts">
  import { Radio } from "flowbite-svelte";

  export let date: Date | null;
  export let defaultLabel: string;

  // datetime-local html input expects a simple 2024-06-30T16:30 format
  const pad2d = (s: number) => s.toString().padStart(2, "0");
  const encodeDatetimeLocal = (d: Date) =>
    `${d.getFullYear()}-${pad2d(d.getMonth() + 1)}-${pad2d(d.getDate())}T${pad2d(d.getHours())}:${pad2d(d.getMinutes())}`;

  let editedDatestring = encodeDatetimeLocal(date || new Date());

  const parseEditedDatetime = () => {
    let parsedDate = new Date(editedDatestring);
    if (parsedDate.toString() === "Invalid Date") {
      date = null;
    } else {
      date = parsedDate;
    }
  };

  const name = "optional-date" + crypto.randomUUID();
  const group = date === null ? "default" : "explicit";
</script>

<Radio
  {name}
  value="default"
  {group}
  on:change={() => {
    date = null;
  }}>{defaultLabel}</Radio
>
<Radio {name} {group} value="explicit" on:change={parseEditedDatetime}>
  <input
    type="datetime-local"
    bind:value={editedDatestring}
    on:change={() => {
      if (date !== null) {
        parseEditedDatetime();
      }
    }}
  />
</Radio>

<style>
  input {
    padding: 0.3rem 0.5rem;
  }
</style>
