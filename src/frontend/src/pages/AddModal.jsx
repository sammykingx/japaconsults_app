import React, { useState } from "react";
// import logo from "../images/logo.png";
// import { Link } from "react-router-dom";
import "../css/AddModal.css";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { AiOutlineClose } from "react-icons/ai";

const AddModal = ({ handleShowAddModal, token }) => {
  const navigate = useNavigate();
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(false); // Added loading state

  const handleLogin = async (e) => {
    setIsLoading(true);
    e.preventDefault();
    if (!content) {
      return toast.error("PLEASE FILL ALL FIELDS");
    }

    try {
      let form = {
        content: content,
        date_created: new Date(),
      };

      // Get the token from your session storage or wherever it's stored

      const response = await axios.post(
        "http://test.sammykingx.tech/drafts/save",
        form,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      toast.success("DRAFT CREATED");
      handleShowAddModal();
      window.location.reload();
      console.log("Draft created successfully:", response.data);
    } catch (error) {
      toast.error("DRAFT CREATION FAILED");
      console.error("Error creating draft:", error);
    } finally {
      setIsLoading(false); // Set loading state back to false when the request is done
    }
  };

  return (
    <div className="modal-form">
      <form onSubmit={handleLogin}>
        <h3>CREATE DRAFT</h3>
        <AiOutlineClose onClick={handleShowAddModal} />
        <div>
          <label htmlFor="content">Draft Content</label>
          <textarea
            id="content"
            name="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "CREATING DRAFT..." : "CREATE DRAFT"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddModal;
