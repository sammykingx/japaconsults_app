import React from "react";
import "../css/Modal.css";
import { AiOutlineClose } from "react-icons/ai";

const Upload = ({ handleModal }) => {
  return (
    <div className="modal-form">
      <form>
        <h3>UPLOAD FILE</h3>
        <div>
          <label htmlFor="">Upload File</label>
          <input type="file" />
        </div>
        <div>
          <button>UPLOAD</button>
        </div>
        <AiOutlineClose onClick={handleModal} />
      </form>
    </div>
  );
};

export default Upload;
