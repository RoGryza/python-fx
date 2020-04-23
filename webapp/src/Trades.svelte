<script>
  import { getContext } from 'svelte';
  import NewTrade from './NewTrade.svelte';

  export let trades_future;
  export let create_trade = () => {};

  const modal = getContext('fx-modal');
  function openNewTrade() {
    modal.open(NewTrade, {
      callback: async (t) => {
        await create_trade({
          sell_ccy: t.sell_ccy,
          sell_amount: t.sell_amount,
          buy_ccy: t.buy_ccy,
          rate: t.rate,
        });
      },
    });
  }
</script>

<h1>Booked Trades</h1>

<button on:click={openNewTrade}>New Trade</button>
<table>
  <thead>
    <th>Sell CCY</th>
    <th>Sell Amount</th>
    <th>Buy CCY</th>
    <th>Buy Amount</th>
    <th>Rate</th>
    <th>Date Booked</th>
  </thead>
  <tbody>
    {#await trades_future}
      <tr>
        <td colspan="6">
          Loading...
        </td>
      </tr>
    {:then trades}
      {#each trades as trade}
        <tr key={trade.id}>
          <td>{ trade.sell_ccy }</td>
          <td>{ (trade.sell_amount / 100).toFixed(2) }</td>
          <td>{ trade.buy_ccy }</td>
          <td>{ (trade.buy_amount / 100).toFixed(2) }</td>
          <td>{ trade.rate }</td>
          <td>{ trade.timestamp }</td>
        </tr>
      {/each}
    {:catch error}
      ERROR {error}
    {/await}
  </tbody>
</table>

<style>
  table {
    border-collapse: collapse;
  }

  table, th, td {
    border: 1px solid black;
    padding: 10px;
  }
</style>

