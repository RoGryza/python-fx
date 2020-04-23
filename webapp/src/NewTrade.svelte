<script>
  import { getContext, onMount } from 'svelte';
  import Api from './api.js';
  import CurrencyInput from './CurrencyInput.svelte';
  import DynamicSelect from './DynamicSelect.svelte';

  let symbols = null;
  let sell_ccy, buy_ccy, rate_future;
  let sell_amount, buy_amount_future;
  let rate, buy_amount;

  const modal = getContext('fx-modal');

  onMount(async() => {
    symbols = await Api.get_symbols();
  });

  $: {
    if (sell_ccy && buy_ccy) {
      rate_future = Api.get_rate(sell_ccy, buy_ccy);
    }
  }

  $: {
    if (rate_future && sell_amount) {
      let orig_rate_future = rate_future;
      buy_amount_future = rate_future.then((newRate) => {
        if (rate_future === orig_rate_future) {
          rate = newRate;
          buy_amount = (rate * sell_amount).toFixed(2);
          return buy_amount;
        }
      });
    }
  }

  // We use a callback instead of an event because we can't attach events to the dynamically
  // created modal, but we can set its props.
  export let callback = () => {};
  function submit() {
    if (!rate || !buy_amount) return;
    modal.close();
    callback({
      sell_ccy,
      sell_amount: Math.floor(sell_amount * 100),
      buy_ccy,
      buy_amount: buy_amount,
      rate,
      timestamp: new Date(),
    });
  }
</script>

<form on:submit|preventDefault={submit}>
  <h2>New Trade</h2>

  <div class="content">
    <label class="cell">
      Sell Currency
      <DynamicSelect options={symbols} bind:value={sell_ccy}/>
    </label>

    <label class="cell">
      Rate
      {#if rate_future}
        {#await rate_future then rate}
          {rate}
        {:catch error}
          {error}
        {/await}
      {/if}
    </label>

    <label class="cell">
      Buy Currency
      <DynamicSelect options={symbols} bind:value={buy_ccy}/>
    </label>

    <label class="cell">
      Sell Amount
      <CurrencyInput bind:value={sell_amount}/>
    </label>

    <div class="cell"/>

    <label class="cell">
      Buy Amount
      {#if buy_amount_future}
        {#await buy_amount_future}
          <input name="buy_amount" readonly/>
        {:then amt}
          <input name="buy_amount" readonly value={amt}/>
        {:catch error}
          {error}
        {/await}
      {:else}
        <input name="buy_amount" readonly/>
      {/if}
    </label>
  </div>

  <div class="bottom-dock">
    <input type="submit" value="Create"/>
    <button on:click|preventDefault={modal.close}>
      Cancel
    </button>
  </div>
</form>

<style>
  .content {
    display: flex;
    flex-wrap: wrap;
    padding: 0;
  }

  .cell {
    flex-grow: 1;
    width: 33.3333%;
  }

  .bottom-dock {
    text-align: right;
  }

  .bottom-dock button {
    margin: 12px;
  }
</style>
