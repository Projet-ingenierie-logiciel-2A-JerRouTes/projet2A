// Exemple d'appel dans React
const fetchRecipes = async (ing) => {
  const response = await fetch(`http://localhost:8000/api/recipes?ingredients=${ing}`);
  const data = await response.json();
  setRecipes(data);
  console.log("bonjour")
  console.log(data)
};