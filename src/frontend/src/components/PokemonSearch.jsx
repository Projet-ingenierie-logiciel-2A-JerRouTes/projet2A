import React, { useState } from "react";
import axios from "axios";
import "../styles/PokemonSearch.css";
import API from "../api/apiClient.js";

function PokemonSearch({ setPokemon }) {
  const [searchTerm, setSearchTerm] = useState("");

  const handleSearch = async () => {
      if (!searchTerm.trim()) {
        alert("Veuillez entrer un nom ou un ID de Pokémon.");
        return;
      }
  
      try {
        const response = await API.get(`pokemon/${searchTerm.toLowerCase()}`);
        setPokemon(response.data);
      } catch (error) {
        const errorMessage = error.response
          ? `Erreur ${error.response.status}: ${
              error.response.data || "Erreur inconnue"
            }`
          : "Erreur de réseau";
        alert(errorMessage);
      }
    };

  return (
    <div className="pokemon-search">
      <label htmlFor="search-input">Rechercher un Pokémon :</label>
      <div className="search-container">
        <input
          id="search-input"
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Entrez un nom ou un ID"
        />
        <button id="search-button" onClick={handleSearch}>
          Chercher
        </button>
      </div>
    </div>
  );
}

export default PokemonSearch;