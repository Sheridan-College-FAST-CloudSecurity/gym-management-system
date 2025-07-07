// src/components/members/MemberForm.jsx
import { useState } from 'react';

export default function MemberForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    membershipType: 'basic'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/members', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!response.ok) throw new Error('Registration failed');
      alert('Member registered successfully!');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Full Name"
        className="w-full p-2 border rounded"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        required
      />
      <select
        className="w-full p-2 border rounded"
        value={formData.membershipType}
        onChange={(e) => setFormData({...formData, membershipType: e.target.value})}
      >
        <option value="basic">Basic Membership</option>
        <option value="premium">Premium Membership</option>
      </select>
      <button type="submit" className="bg-blue-500 text-white p-2 rounded">
        Register Member
      </button>
    </form>
  );
}