<script>
  import { setContext } from 'svelte';
  import { sineInOut, backOut } from 'svelte/easing';

  let Component = null;
  let props = {};

  // We don't use the built-in fade because it sets the element's opacity, which affects its
  // children. We manipulate the overlay background color instead.
  function fade(node, { duration }) {
    return {
      duration,
      css: (t, u) => `background-color: rgba(0, 0, 0, ${sineInOut(t * 0.4)})`,
    };
  }

  function grow(node, { duration }) {
    return {
      duration,
      css: t => `transform: scale(${backOut(t)})`,
    };
  }

  function open(NewComponent, newProps = {}) {
    Component = NewComponent;
    props = newProps;
  }

  function close() {
    Component = null;
  }

  setContext('fx-modal', { open, close });
</script>

<slot/>

{#if Component}
  <div class="overlay" transition:fade={{duration: 350}}>
    <div class="modal" transition:grow={{duration: 350}}>
      <button class="close" on:click={close}>&times;</button>
      <div>
        <svelte:component this={Component} {...props}/>
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100vw;
    height: 100vh;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.4);
  }

  .modal {
    background-color: #fefefe;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 700px;
  }

  .close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
  }

  .close:hover,
  .close:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
  }

  .close, .close:hover, .close:focus, .close:active {
    background: none;
    border: none;
    outline: none;
  }
</style>
