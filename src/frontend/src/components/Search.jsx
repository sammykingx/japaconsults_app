import { useState } from "react";

const Search = (initialData) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(initialData || []);

  const handleInputChange = (event) => {
    const searchTerm = event.target.value;
    setQuery(searchTerm);
    if (searchTerm === "") {
      setResults(initialData || []);
    } else {
      search(searchTerm);
    }
  };

  const search = (query) => {
    const filteredResults =
      (initialData &&
        initialData.filter(
          (item) =>
            (item.filename &&
              item.filename.toLowerCase().includes(query.toLowerCase())) ||
            (item.content &&
              item.content.toLowerCase().includes(query.toLowerCase())) ||
            (item.username &&
              item.username.toLowerCase().includes(query.toLowerCase()))
        )) ||
      [];

    setResults(filteredResults);
    console.log(filteredResults);
  };

  return { query, results, handleInputChange };
};

export default Search;
