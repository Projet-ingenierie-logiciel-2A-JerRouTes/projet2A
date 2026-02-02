import React from "react";
import "../styles/PokemonDetails.css";
import typeColors from "../styles/typeColors.js";

function PokemonDetails({ pokemon }) {
  if (!pokemon) return <p></p>;

  return (
    <div className="pokemon-details">
      <h2 id="pokemon-name">
        {pokemon.name.toUpperCase()} <span id="pokemon-id">#{pokemon.id}</span>
      </h2>

      <div className="img-container">
        <img
          id="sprite"
          src={pokemon.sprites.front_default}
          alt={pokemon.name}
        />
      </div>

      <div className="pokemon-attributes">
        <p id="weight">Poids : {pokemon.weight / 10} kg</p>
        <p id="height">Taille : {pokemon.height / 10} m</p>
      </div>

      <div id="types" className="pokemon-types">
        {pokemon.types.map((typeInfo) => (
          <span
            key={typeInfo.type.name}
            className="pokemon-type"
            style={{ backgroundColor: typeColors[typeInfo.type.name] }}
          >
            {typeInfo.type.name.toUpperCase()}
          </span>
        ))}
      </div>

      <div className="pokemon-stats">
        <h3>Statistiques</h3>
        <p id="hp">
          PV : {pokemon.stats.find((stat) => stat.stat.name === "hp").base_stat}
        </p>
        <p id="attack">
          Attaque :{" "}
          {pokemon.stats.find((stat) => stat.stat.name === "attack").base_stat}
        </p>
        <p id="defense">
          Défense :{" "}
          {pokemon.stats.find((stat) => stat.stat.name === "defense").base_stat}
        </p>
        <p id="special-attack">
          Attaque Spéciale :{" "}
          {
            pokemon.stats.find((stat) => stat.stat.name === "special-attack")
              .base_stat
          }
        </p>
        <p id="special-defense">
          Défense Spéciale :{" "}
          {
            pokemon.stats.find((stat) => stat.stat.name === "special-defense")
              .base_stat
          }
        </p>
        <p id="speed">
          Vitesse :{" "}
          {pokemon.stats.find((stat) => stat.stat.name === "speed").base_stat}
        </p>
      </div>
    </div>
  );
}

export default PokemonDetails;