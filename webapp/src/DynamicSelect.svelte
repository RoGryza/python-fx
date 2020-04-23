<script>
  export let options = null;
  export let value = null;
</script>

<select bind:value required
  disabled={options === null} class:loading={options === null}
  {...$$restProps}>
  <option hidden value></option>
  {#if options !== null}
    {#each options as option}
      <option>{option}</option>
    {/each}
  {/if}
</select>

<style>
  select.loading {
    cursor: wait;
  }
</style>
