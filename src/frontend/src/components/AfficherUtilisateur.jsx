import React from "react";
import { Eye, Edit, Trash2, Undo2, Lock, User, Mail, Database } from "lucide-react";

const AfficherUtilisateur = ({ utilisateur, on_back, on_edit, on_delete }) => {
  if (!utilisateur) return null;

  return (
    <div className="carte-centrale gestion-panel">
      {/* 1. TITRE EN PREMIER (Noir) */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <h1 className="titre-principal" style={{ color: "#000000", fontSize: "2.5rem", fontWeight: "800" }}>
          Utilisateur : {utilisateur.username}
        </h1>
      </div>

      {/* 2. BOUTONS EN DESSOUS (Zone pointillée) */}
      <div style={{ 
        border: "1px dashed #cbd5e1", 
        borderRadius: "12px", 
        padding: "15px", 
        display: "flex", 
        justifyContent: "center", 
        gap: "15px",
        marginBottom: "30px",
        backgroundColor: "rgba(248, 250, 252, 0.5)"
      }}>
        <button 
          className="bouton-action btn-recette-style" 
          onClick={() => on_edit(utilisateur.user_id)}
        >
          <Edit size={18} /> Modifier l'utilisateur
        </button>
        <button 
          className="bouton-action btn-stock-style" 
          onClick={() => on_delete(utilisateur.user_id)}
        >
          <Trash2 size={18} /> Supprimer l'utilisateur
        </button>
      </div>

      {/* 3. DÉTAILS */}
      <div className="details-container" style={{ padding: "0 20px", display: "grid", gap: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <User size={20} color="#64748b" />
          <span style={{ fontSize: "1.1rem" }}><strong>Pseudo :</strong> {utilisateur.username}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Mail size={20} color="#64748b" />
          <span style={{ fontSize: "1.1rem" }}><strong>Email :</strong> {utilisateur.email}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Lock size={20} color="#64748b" />
          <span style={{ fontSize: "1.1rem" }}>
            <strong>Mot de passe :</strong> <span style={{ fontStyle: "italic", color: "#94a3b8", marginLeft: "8px" }}>********</span>
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Database size={20} color="#64748b" />
          <span style={{ fontSize: "1.1rem" }}><strong>ID Stock :</strong> <span style={{ color: "#cbd5e1" }}>Vide</span></span>
        </div>
        <div style={{ textAlign: "center", marginTop: "10px" }}>
          <span className={`badge-role ${utilisateur.status === "admin" ? "bg-admin" : "bg-user"}`}>
            {utilisateur.status}
          </span>
        </div>
      </div>

      {/* 4. BOUTON RETOUR */}
      <div style={{ display: "flex", justifyContent: "center", marginTop: "40px" }}>
        <button className="bouton-retour-gestion" onClick={on_back}>
          <Undo2 size={18} /> Retour à la liste
        </button>
      </div>
    </div>
  );
};

export default AfficherUtilisateur;