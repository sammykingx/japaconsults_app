import React, { useState } from "react";
// import logo from "../images/logo.png";
// import { Link } from "react-router-dom";
import "../css/AddModal.css";
import axios from "axios";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { AiOutlineClose } from "react-icons/ai";
import jwt_decode from "jwt-decode";

const UpdateModal = ({ handleShowUpdateModal, token, draft }) => {
  const navigate = useNavigate();
  const [content, setContent] = useState(draft.content);
  const [isLoading, setIsLoading] = useState(false); // Added loading state
  const handleLogin = async (e) => {
    setIsLoading(true);
    e.preventDefault();
    if (!content) {
      return toast.error("PLEASE FILL ALL FIELDS");
    }

    const user_id = jwt_decode(token).sub;

    try {
      let form = {
        draft_id: draft.draft_id,
        user_id: user_id,
        content: content,
        title: "",
        doc_url: [null],
        date_created: draft.date_created,
        last_updated: new Date(),
      };

      // Get the token from your session storage or wherever it's stored

      const response = await axios.put(
        "http://test.sammykingx.tech/drafts/update",
        form,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      toast.success("DRAFT UPDATED");
      handleShowUpdateModal();
      window.location.reload();
      console.log("Draft updated successfully:", response.data);
    } catch (error) {
      toast.error("DRAFT CREATION FAILED");
      console.error("Error updated draft:", error);
    } finally {
      setIsLoading(false); // Set loading state back to false when the request is done
    }
  };

  return (
    <div className="modal-form" style={{ background: "rgba(0,0,0,0.5)" }}>
      <form onSubmit={handleLogin}>
        <h3>UPDATE DRAFT</h3>
        <AiOutlineClose onClick={handleShowUpdateModal} />
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
            {isLoading ? "UPDATING DRAFT..." : "UPDATE DRAFT"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default UpdateModal;
