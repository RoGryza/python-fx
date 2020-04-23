export default {
  get_trades: async function() {
    const resp = await fetch('/api/trades');
    const {trades} = await resp.json();
    return trades;
  },

  create_trade: async function(trade) {
    const resp = await fetch('/api/trades', {
      method: 'POST',
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(trade),
    });
    return await resp.json();
  },

  get_symbols: async function() {
    const resp = await fetch('/api/symbols');
    const {symbols} = await resp.json();
    return symbols;
  },

  get_rate: async function(from, to) {
    const resp = await fetch(
      '/api/rate?from_symbol=' + from + "&to_symbol=" + to
    );
    const {rate} = await resp.json();
    return rate;
  },
};
