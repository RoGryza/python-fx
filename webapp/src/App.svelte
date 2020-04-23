<script>
  import { onMount } from 'svelte';
  import Api from './api.js';
  import Modal from './Modal.svelte';
  import Trades from './Trades.svelte';

  let trades_future = Promise.resolve([]);
  function refresh() {
    trades_future = Api.get_trades();
  }

  onMount(refresh);

  async function create_trade(trade) {
    const result = await Api.create_trade(trade);
    refresh();
    return result;
  }
</script>

<Modal>
  <main>
    <Trades {trades_future} {create_trade}/>
  </main>
</Modal>
