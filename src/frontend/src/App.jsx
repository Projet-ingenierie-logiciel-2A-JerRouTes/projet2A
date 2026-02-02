import React, { useState } from "react";
import PokemonSearch from "./components/PokemonSearch";
import PokemonDetails from "./components/PokemonDetails";
import "./App.css";

const App = () => {
  const [pokemon, setPokemon] = useState(null);

  return (
    <div className="app">
      <h1>Pokédex</h1>
      <PokemonSearch setPokemon={setPokemon} />
      <PokemonDetails pokemon={pokemon} />
    </div>
  );
};

export default App;