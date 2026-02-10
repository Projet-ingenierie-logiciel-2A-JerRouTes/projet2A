import React, { useState } from "react";
import PokemonSearch from "./components/PokemonSearch";
import PokemonDetails from "./components/PokemonDetails";
import Test from "./components/Test";
import "./App.css";

const App = () => {
  const [pokemon, setPokemon] = useState(null);

  return (
    <div className="app">
      <h1>Frigo App</h1>
      <Test />

      {/*<PokemonSearch setPokemon={setPokemon} />
      <PokemonDetails pokemon={pokemon} /> */}
    </div>
  );
};

export default App;
