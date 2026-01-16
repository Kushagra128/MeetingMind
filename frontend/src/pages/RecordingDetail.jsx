import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import {
	ArrowLeft,
	Download,
	FileText,
	Clock,
	Calendar,
	Play,
	Pause,
	Volume2,
} from "lucide-react";

const RecordingDetail = () => {
	const { id } = useParams();
	const navigate = useNavigate();

	const [recording, setRecording] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [activeTab, setActiveTab] = useState("transcript");

	// Audio
	const [isPlaying, setIsPlaying] = useState(false);
	const [audioProgress, setAudioProgress] = useState(0);
	const audioRef = useRef(null);

	// Filename inputs for PDFs
	const [transcriptFilename, setTranscriptFilename] =
		useState("transcript.pdf");
	const [summaryFilename, setSummaryFilename] = useState("summary.pdf");

	useEffect(() => {
		fetchRecording();
	}, [id]);

	// Fetch audio with token
	useEffect(() => {
		if (recording?.audio_file_path && audioRef.current) {
			const token = localStorage.getItem("token");
			if (!token) return;

			const audioUrl = `/api/recordings/${id}/audio`;

			fetch(audioUrl, {
				headers: { Authorization: `Bearer ${token}` },
			})
				.then((res) => res.blob())
				.then((blob) => {
					const url = URL.createObjectURL(blob);
					audioRef.current.src = url;
					audioRef.current.load();
				})
				.catch((err) => {
					console.error("Audio load error:", err);
					setError("Failed to load audio file");
				});
		}
	}, [recording]);

	const fetchRecording = async () => {
		try {
			const res = await axios.get(`/api/recordings/${id}`);
			setRecording(res.data.recording);
		} catch (err) {
			console.error(err);
			setError("Failed to load recording");
		} finally {
			setLoading(false);
		}
	};

	const formatDate = (d) => {
		const date = new Date(d);
		return (
			date.toLocaleDateString() +
			" " +
			date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
		);
	};

	const formatDuration = (sec) => {
		if (!sec) return "N/A";
		const m = Math.floor(sec / 60);
		const s = Math.floor(sec % 60);
		return `${m}:${s.toString().padStart(2, "0")}`;
	};

	const togglePlayback = () => {
		if (!audioRef.current) return;

		if (isPlaying) {
			audioRef.current.pause();
			setIsPlaying(false);
		} else {
			audioRef.current.play();
			setIsPlaying(true);
		}
	};

	// Update playback progress
	useEffect(() => {
		const audio = audioRef.current;
		if (!audio) return;

		const update = () => {
			if (audio.duration) {
				setAudioProgress((audio.currentTime / audio.duration) * 100);
			}
		};

		const end = () => {
			setIsPlaying(false);
			setAudioProgress(0);
		};

		audio.addEventListener("timeupdate", update);
		audio.addEventListener("ended", end);

		return () => {
			audio.removeEventListener("timeupdate", update);
			audio.removeEventListener("ended", end);
		};
	}, []);

	// 🚀 Download helper (always authenticated)
	const downloadPDF = async (type, filename) => {
		try {
			const token = localStorage.getItem("token");
			if (!token) {
				alert("Login again — missing authentication.");
				return;
			}

			const url = `/api/recordings/${id}/pdf/${type}`;

			const res = await fetch(url, {
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});

			if (!res.ok) {
				alert(`Failed to download (${res.status})`);
				return;
			}

			const blob = await res.blob();

			const link = document.createElement("a");
			link.href = window.URL.createObjectURL(blob);
			link.download = filename || `${type}.pdf`;
			link.click();

			window.URL.revokeObjectURL(link.href);
		} catch (err) {
			console.error(err);
			alert("Failed to download PDF.");
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-gray-50">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
			</div>
		);
	}

	if (error || !recording) {
		return (
			<div className="min-h-screen bg-gray-50 p-6">
				<div className="max-w-xl mx-auto bg-red-50 p-6 rounded border border-red-200">
					{error || "Recording not found"}
				</div>
				<button
					onClick={() => navigate("/dashboard")}
					className="mt-4 text-primary-600 flex items-center"
				>
					<ArrowLeft className="w-4 h-4 mr-1" /> Back
				</button>
			</div>
		);
	}

	// -------------------------
	// UI STARTS
	// -------------------------
	return (
		<div className="min-h-screen bg-gray-50">
			{/* HEADER */}
			<header className="bg-white shadow-sm">
				<div className="max-w-7xl mx-auto p-4 flex items-center justify-between">
					<button
						onClick={() => navigate("/dashboard")}
						className="flex items-center text-gray-600 hover:text-gray-900"
					>
						<ArrowLeft className="w-5 h-5 mr-2" />
						Back
					</button>
					<h1 className="text-2xl font-bold">{recording.title}</h1>
					<div className="w-40"></div>
				</div>
			</header>

			{/* MAIN */}
			<main className="max-w-7xl mx-auto p-6">
				{/* INFO SECTION */}
				<div className="bg-white shadow p-6 rounded mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
					<div className="flex items-center space-x-3">
						<Calendar className="w-5 h-5 text-gray-400" />
						<div>
							<p className="text-sm text-gray-500">Created</p>
							<p className="font-medium">{formatDate(recording.created_at)}</p>
						</div>
					</div>
					<div className="flex items-center space-x-3">
						<Clock className="w-5 h-5 text-gray-400" />
						<div>
							<p className="text-sm text-gray-500">Duration</p>
							<p className="font-medium">
								{formatDuration(recording.duration)}
							</p>
						</div>
					</div>
					<div className="flex items-center space-x-3">
						<FileText className="w-5 h-5 text-gray-400" />
						<div>
							<p className="text-sm text-gray-500">Status</p>
							<p
								className={`font-medium ${
									recording.status === "completed"
										? "text-green-600"
										: recording.status === "processing"
										? "text-yellow-600"
										: "text-red-600"
								}`}
							>
								{recording.status}
							</p>
						</div>
					</div>
				</div>

				{/* AUDIO PLAYER */}
				{recording.audio_file_path && (
					<div className="bg-white p-6 shadow rounded mb-6">
						<h2 className="text-lg font-semibold mb-4 flex items-center">
							<Volume2 className="w-5 h-5 mr-2" />
							Audio Playback
						</h2>

						<audio ref={audioRef} className="hidden" />

						<div className="flex items-center space-x-4">
							<button
								onClick={togglePlayback}
								className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center"
							>
								{isPlaying ? (
									<Pause className="w-6 h-6" />
								) : (
									<Play className="w-6 h-6 ml-1" />
								)}
							</button>

							<div className="flex-1">
								<div className="w-full bg-gray-200 h-2 rounded-full">
									<div
										className="bg-primary-600 h-2 rounded-full"
										style={{ width: `${audioProgress}%` }}
									></div>
								</div>
							</div>
						</div>
					</div>
				)}

				{/* PDF DOWNLOAD SECTION */}
				<div className="bg-white shadow p-6 rounded mb-6">
					<h2 className="text-lg font-semibold mb-4">Download PDFs</h2>

					<div className="grid md:grid-cols-2 gap-6">
						{/* Transcript */}
						{recording.transcript_pdf_path && (
							<div>
								<label className="text-sm font-medium">
									Transcript filename
								</label>
								<input
									type="text"
									value={transcriptFilename}
									onChange={(e) => setTranscriptFilename(e.target.value)}
									className="border p-2 rounded w-full mt-1 mb-3"
									placeholder="transcript.pdf"
								/>
								<button
									onClick={() => downloadPDF("transcript", transcriptFilename)}
									className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700"
								>
									<Download className="w-4 h-4" />
									<span>Download Transcript PDF</span>
								</button>
							</div>
						)}

						{/* Summary */}
						{recording.summary_pdf_path && (
							<div>
								<label className="text-sm font-medium">Summary filename</label>
								<input
									type="text"
									value={summaryFilename}
									onChange={(e) => setSummaryFilename(e.target.value)}
									className="border p-2 rounded w-full mt-1 mb-3"
									placeholder="summary.pdf"
								/>
								<button
									onClick={() => downloadPDF("summary", summaryFilename)}
									className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700"
								>
									<Download className="w-4 h-4" />
									<span>Download Summary PDF</span>
								</button>
							</div>
						)}
					</div>
				</div>

				{/* TRANSCRIPT + SUMMARY TABS */}
				<div className="bg-white rounded shadow">
					<div className="border-b flex">
						<button
							className={`px-6 py-4 border-b-2 ${
								activeTab === "transcript"
									? "border-primary-500 text-primary-600"
									: "border-transparent text-gray-500"
							}`}
							onClick={() => setActiveTab("transcript")}
						>
							Transcript
						</button>
						<button
							className={`px-6 py-4 border-b-2 ${
								activeTab === "summary"
									? "border-primary-500 text-primary-600"
									: "border-transparent text-gray-500"
							}`}
							onClick={() => setActiveTab("summary")}
						>
							Summary
						</button>
					</div>

					<div className="p-6">
						{activeTab === "transcript" && (
							<pre className="whitespace-pre-wrap bg-gray-50 p-6 rounded">
								{recording.transcript || "No transcript available"}
							</pre>
						)}

						{activeTab === "summary" && (
							<pre className="whitespace-pre-wrap bg-gray-50 p-6 rounded">
								{recording.summary || "No summary available"}
							</pre>
						)}
					</div>
				</div>
			</main>
		</div>
	);
};

export default RecordingDetail;
