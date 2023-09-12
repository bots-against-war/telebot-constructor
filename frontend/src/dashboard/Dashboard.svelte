<script>
  import { Route } from "svelte-routing";
  import CreateBotButton from "../CreateBotButton.svelte";
  import ArrayBots from "../components/ArrayBots.svelte";
  // @ts-expect-error
  import Modal from "svelte-simple-modal";
</script>

<Route path="/">
  <div style="display:flex; flex-flow: column; height:100%;">
    <div class="center, text">
      <p>
        Добро пожаловать в B.A.W., современный конструктор чат-ботов, который поможет вашей инициативе стать еще ближе к
        пользователям.
      </p>
    </div>
    <div class="center">
      <Modal><CreateBotButton /></Modal>
    </div>
    <div class="center">
      <ArrayBots />
    </div>
  </div>
</Route>
<Route path="/command">
  <div class="center, text">
    <p>Команда</p>
  </div>
</Route>
<Route path="/actions">
  <div class="center, text">
    <p>Действия</p>
  </div>
</Route>
<Route path="/security">
  <div class="center, text">
    <p>Безопасность</p>
  </div>
</Route>
