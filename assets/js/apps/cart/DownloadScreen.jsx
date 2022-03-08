import React from "react";
import { BsChevronLeft } from "react-icons/bs";
import { Link } from "react-router-dom";

export default function DownloadScreen() {
    return (
        <div>
            <div className="mb-3">
                <Link to="/"><BsChevronLeft />Go back</Link>
            </div>
            <h1 className="mb-2 h4 text-secondary font-weight-light">Request download</h1>
            <h2 className="mb-4 h1">Download request not yet supported</h2>
            <p>MyTardis does not yet support downloading cart contents larger than 5GB.</p>
            <p>Please try removing items from the cart and try again. Alternatively, you can download larger objects individually.</p>
            <Link to="/" className="mt-2 btn btn-primary">Go to Cart</Link>
        </div>
    );
}
